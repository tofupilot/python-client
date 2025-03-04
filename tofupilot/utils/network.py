from typing import Dict, List, Optional, Any, Union, Callable
import os
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Default retry configuration
DEFAULT_TIMEOUT = 30  # Reduced from 60 seconds
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5
DEFAULT_STATUS_FORCELIST = [500, 502, 503, 504]

# Create a session with retry logic
def create_session(
    retries: int = DEFAULT_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    status_forcelist: List[int] = None,
) -> requests.Session:
    """
    Create a requests session with retry logic
    """
    if status_forcelist is None:
        status_forcelist = DEFAULT_STATUS_FORCELIST

    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Request timeout decorator
def timeout_decorator(seconds: int = DEFAULT_TIMEOUT) -> Callable:
    """
    Decorator to set a timeout for requests functions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs.setdefault("timeout", seconds)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Global session instance
SESSION = create_session()

@timeout_decorator(DEFAULT_TIMEOUT)
def secure_request(
    method: str,
    url: str,
    **kwargs
) -> requests.Response:
    """
    Make a secure HTTP request with proper error handling and retry logic
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: URL to request
        **kwargs: Additional arguments to pass to requests
    """
    # Ensure SSL verification is enabled
    kwargs.setdefault("verify", True)
    
    # Use session for connection pooling
    response = SESSION.request(method, url, **kwargs)
    response.raise_for_status()
    
    return response


def parse_error_message(response: requests.Response) -> str:
    try:
        error_data = response.json()
        return error_data.get("error", {}).get(
            "message", f"HTTP error occurred: {response.text}"
        )
    except ValueError:
        return f"HTTP error occurred: {response.text}"


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

    warnings = None  # Initialize warnings to None

    # Check if the response body is not empty and Content-Type is application/json
    if (
        http_err.response.text.strip()
        and http_err.response.headers.get("Content-Type") == "application/json"
    ):
        # Parse JSON safely
        response_json = http_err.response.json()
        warnings = response_json.get("warnings")
        if warnings is not None:
            for warning in warnings:
                logger.warning(warning)
        error_message = parse_error_message(http_err.response)
    else:
        # Handle cases where response is empty or non-JSON
        error_message = http_err

    logger.error(error_message)

    return {
        "success": False,
        "message": None,
        "warnings": warnings,
        "status_code": http_err.response.status_code,
        "error": {"message": error_message},
    }


def handle_network_error(logger, e: requests.RequestException) -> Dict[str, Any]:
    """Handles network errors and logs them."""
    logger.error(f"Network error: {e}")
    return {
        "success": False,
        "message": None,
        "warnings": None,
        "status_code": None,
        "error": {"message": str(e)},
    }
