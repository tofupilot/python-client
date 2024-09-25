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
    logger, response: requests.Response, with_data: bool = None
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

    if with_data is not None and with_data:
        data = json_response.get("data")
        return_response["data"] = data

    return return_response


def handle_http_error(
    logger, http_err: requests.exceptions.HTTPError
) -> Dict[str, Any]:
    """Handles HTTP errors and logs them."""

    warnings: Optional[List[str]] = http_err.response.json().get("warnings")
    if warnings is not None:
        for warning in warnings:
            logger.warning(warning)

    error_message = parse_error_message(http_err.response)
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


def handle_unexpected_error(logger, e: Exception) -> Dict[str, Any]:
    """Handles unexpected errors and logs them."""
    error_message = f"An unexpected error occurred: {e}"
    logger.error(error_message)
    return {
        "success": False,
        "message": None,
        "status_code": None,
        "warnings": None,
        "error": {"message": error_message},
    }
