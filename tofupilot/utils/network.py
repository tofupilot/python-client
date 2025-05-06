from typing import Dict, List, Optional, Any

import requests
from ..constants.requests import SECONDS_BEFORE_TIMEOUT


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
    verify: str | None = None,
) -> Dict:
    """Unified API request handler with consistent error handling"""
    try:
        response = requests.request(
            method, url, 
            json=data,
            headers=headers,
            params=params,
            timeout=timeout,
            verify=verify,
        )
        response.raise_for_status()
        return handle_response(logger, response)
    except requests.exceptions.HTTPError as http_err:
        return handle_http_error(logger, http_err)
    except requests.RequestException as e:
        return handle_network_error(logger, e)


def handle_response(
    logger,
    response: requests.Response,
) -> dict:
    """
    Processes a successful response from the server.
    Logs any warnings or success messages, then returns the parsed data.
    """
    data = response.json()

    # Logging warnings if present
    warnings: Optional[List[str]] = data.get("warnings")
    if warnings is not None:
        for warning in warnings:
            logger.warning(warning)

    # Logging success message if the JSON has one
    message = data.get("message")
    if message is not None:
        logger.success(message)

    # Returning the parsed JSON to the caller
    return data


def handle_http_error(
    logger, http_err: requests.exceptions.HTTPError
) -> Dict[str, Any]:
    """Handles HTTP errors and logs them."""
    warnings = None
    
    # Extract error details from JSON response when available
    if (http_err.response.text.strip() and 
        http_err.response.headers.get("Content-Type") == "application/json"):
        try:
            response_json = http_err.response.json()
            warnings = response_json.get("warnings")
            if warnings:
                for warning in warnings:
                    logger.warning(warning)
            error_message = parse_error_message(http_err.response)
        except ValueError:
            error_message = str(http_err)
    else:
        error_message = str(http_err)

    # Log the error through the logger for proper formatting
    logger.error(error_message)

    # Return structured error info
    return {
        "success": False,
        "message": None,
        "warnings": warnings,
        "status_code": http_err.response.status_code,
        "error": {"message": error_message},
    }


def handle_network_error(logger, e: requests.RequestException) -> Dict[str, Any]:
    """Handles network errors and logs them."""
    error_message = f"Network error: {str(e)}"
    logger.error(error_message)
    
    # Provide SSL-specific guidance
    if isinstance(e, requests.exceptions.SSLError) or "SSL" in str(e) or "certificate verify failed" in str(e):
        logger.warning("SSL certificate verification error detected")
        logger.warning("This is typically caused by missing or invalid SSL certificates")
        logger.warning("Try: 1) pip install certifi  2) /Applications/Python*/Install Certificates.command")
    
    # Return structured error info
    return {
        "success": False,
        "message": None,
        "warnings": None,
        "status_code": None,
        "error": {"message": str(e)},
    }
