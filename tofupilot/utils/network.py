from typing import Dict, List, Optional, Any

import requests


def parse_error_message(response: requests.Response) -> str:
    try:
        error_data = response.json()
        return error_data.get("error", {}).get(
            "message", f"HTTP error occurred: {response.text}"
        )
    except ValueError:
        return f"HTTP error occurred: {response.text}"


def handle_response(
    logger, response: requests.Response, additional_field: Optional[str] = None
) -> Dict[str, Any]:
    """Processes the response from the server and logs necessary information."""
    json_response = response.json()
    warnings: Optional[List[str]] = json_response.get("warnings")
    if warnings is not None:
        for warning in warnings:
            logger.warning(warning)

    message = json_response.get("message")
    if message is not None:
        logger.success(message)

    return_response = {
        "success": True,
        "message": message,
        "warnings": warnings,
        "status_code": response.status_code,
        "error": None,
    }

    if additional_field:
        additional_data = json_response.get(additional_field)
        if additional_data is not None:
            return_response[additional_field] = additional_data

    return return_response


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
