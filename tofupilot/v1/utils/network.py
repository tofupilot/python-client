from typing import Dict, List, Optional, Any, Union
import tempfile
import os

import requests
import certifi
import posthog
from ..constants.requests import SECONDS_BEFORE_TIMEOUT
from ..responses import HttpErrorResponse, NetworkErrorResponse, ErrorResponse

# Cache for certificate bundles to avoid recreating them
_cert_bundle_cache = {}

def prepare_verify_setting(verify: Optional[str]) -> str:
    """Prepare verify setting for self-signed certificates by creating cached certificate bundle."""
    if verify and isinstance(verify, str) and verify.endswith('.crt'):
        try:
            cert_mtime = os.path.getmtime(verify)
            cache_key = f"{verify}:{cert_mtime}"
            
            if cache_key in _cert_bundle_cache:
                cached_path = _cert_bundle_cache[cache_key]
                if os.path.exists(cached_path):
                    return cached_path
                else:
                    del _cert_bundle_cache[cache_key]
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as temp_bundle:
                with open(certifi.where(), 'r') as ca_bundle:
                    temp_bundle.write(ca_bundle.read())
                
                with open(verify, 'r') as custom_cert:
                    temp_bundle.write('\n')
                    temp_bundle.write(custom_cert.read())
                
                bundle_path = temp_bundle.name
                _cert_bundle_cache[cache_key] = bundle_path
                return bundle_path
                
        except (OSError, IOError):
            return verify
    
    return verify


def cleanup_temp_cert_bundle(verify_setting: str, original_verify: Optional[str]):
    """Clean up temporary certificate bundle if it was created."""
    pass


def parse_error_message(response: requests.Response) -> str:
    """Extract error message from response"""
    try:
        error_data = response.json()
        return error_data.get("error", {}).get(
            "message", f"HTTP error occurred: {response.text}"
        )
    except ValueError:
        return f"HTTP error occurred: {response.text}"


def api_request(
    logger, method: str, url: str, headers: Dict, 
    data: Optional[Dict] = None, 
    params: Optional[Dict] = None,
    timeout: int = SECONDS_BEFORE_TIMEOUT,
    verify: Optional[str] = None,
) -> Union[Dict[str, Any], ErrorResponse]:
    """Unified API request handler with consistent error handling"""
    verify_setting = prepare_verify_setting(verify)
    
    try:
        response = requests.request(
            method, url, 
            json=data,
            headers=headers,
            params=params,
            timeout=timeout,
            verify=verify_setting,
        )
        response.raise_for_status()
        result = handle_response(logger, response)
        
        return result
    except requests.exceptions.HTTPError as http_err:
        return handle_http_error(logger, http_err)
    except requests.RequestException as e:
        return handle_network_error(logger, e)
    finally:
        cleanup_temp_cert_bundle(verify_setting, verify)


def handle_response(
    logger,
    response: requests.Response,
) -> dict:
    """
    Processes a successful response from the server.
    Logs any warnings or success messages, then returns the parsed data.
    """
    data = response.json()

    # Ensure logger is active to process messages
    was_resumed = False
    if hasattr(logger, 'resume'):
        logger.resume()
        was_resumed = True
    
    try:
        # Process warnings
        warnings: Optional[List[str]] = data.get("warnings")
        if warnings is not None:
            for warning in warnings:
                logger.warning(warning)
        
        # Process errors
        errors = data.get("errors") or data.get("error")
        if errors:
            # Handle both array and single object formats
            if isinstance(errors, list):
                for error in errors:
                    if isinstance(error, dict) and "message" in error:
                        logger.error(error["message"])
                    else:
                        logger.error(str(error))
            elif isinstance(errors, dict) and "message" in errors:
                logger.error(errors["message"])
            elif isinstance(errors, str):
                logger.error(errors)
        
        # Process success message
        message = data.get("message")
        if message is not None:
            logger.success(message)
    except Exception as e:
        posthog.capture_exception(e)
    finally:
        # Restore logger state if needed
        if was_resumed and hasattr(logger, 'pause'):
            logger.pause()

    # Returning the parsed JSON to the caller
    return data


def handle_http_error(
    logger, http_err: requests.exceptions.HTTPError
) -> HttpErrorResponse:
    """Handles HTTP errors and logs them."""

    posthog.capture_exception(http_err)
    warnings = None
    
    # Ensure logger is active to process messages
    was_resumed = False
    if hasattr(logger, 'resume'):
        logger.resume()
        was_resumed = True
    
    try:
        # Extract error details from JSON response when available
        if (http_err.response.text.strip() and 
            http_err.response.headers.get("Content-Type") == "application/json"):
            try:
                response_json = http_err.response.json()
                
                # Process warnings if present
                warnings = response_json.get("warnings")
                if warnings:
                    for warning in warnings:
                        logger.warning(warning)
                        
                # Get error message
                error_message = parse_error_message(http_err.response)
            except ValueError:
                error_message = str(http_err)
        else:
            error_message = str(http_err)

        # Log the error through the logger for proper formatting
        logger.error(error_message)
    except Exception as e:
        posthog.capture_exception(e)
    finally:
        # Restore logger state if needed
        if was_resumed and hasattr(logger, 'pause'):
            logger.pause()

    # Return structured error info
    return {
        "success": False,
        "message": None,
        "warnings": warnings,
        "status_code": http_err.response.status_code,
        "error": {"message": error_message},
    }


def handle_network_error(logger, e: requests.RequestException) -> NetworkErrorResponse:
    """Handles network errors and logs them."""
    posthog.capture_exception(e)
    # Ensure logger is active to process messages
    was_resumed = False
    if hasattr(logger, 'resume'):
        logger.resume()
        was_resumed = True
    
    try:
        error_message = f"Network error: {str(e)}"
        logger.error(error_message)
        
        if isinstance(e, requests.exceptions.SSLError) or "SSL" in str(e) or "certificate verify failed" in str(e):
            if "storage." in str(e) and "certificate is not valid for" in str(e):
                logger.warning("Certificate must include storage subdomain")
                logger.warning("Generate wildcard certificate or add storage hostname to SAN")
            else:
                logger.warning("SSL certificate verification error detected")
                logger.warning("Try: 1) pip install certifi  2) /Applications/Python*/Install Certificates.command")
    except Exception as e2:
        posthog.capture_exception(e2)
    finally:
        # Restore logger state if needed
        if was_resumed and hasattr(logger, 'pause'):
            logger.pause()
    
    # Return structured error info
    return {
        "success": False,
        "message": None,
        "warnings": None,
        "status_code": None,
        "error": {"message": str(e)},
    }
