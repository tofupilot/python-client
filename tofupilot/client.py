from typing import Dict, List, Optional, Any
import requests
import logging
import os
from datetime import datetime, timedelta
from importlib.metadata import version

from .constants import (
    ENDPOINT,
    FILE_MAX_SIZE,
    CLIENT_MAX_ATTACHMENTS,
    SECONDS_BEFORE_TIMEOUT,
)
from .models import SubUnit, UnitUnderTest, Step, Importer
from .utils import (
    check_latest_version,
    validate_files,
    initialize_upload,
    upload_file,
    handle_attachments,
    parse_error_message,
    setup_logger,
    timedelta_to_iso,
    datetime_to_iso,
)


class TofuPilotClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = ENDPOINT):
        self._current_version = version("tofupilot")
        print_version_banner(self._current_version)
        self._api_key = api_key or os.environ.get("TOFUPILOT_API_KEY")
        if self._api_key is None:
            error = "Please set TOFUPILOT_API_KEY environment variable. For more information on how to find or generate a valid API key, visit https://docs.tofupilot.com/user-management#api-key."
            raise Exception(error)

        self._base_url = f"{base_url}/api/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        self._logger = setup_logger(logging.INFO)
        self._max_attachments = CLIENT_MAX_ATTACHMENTS
        self._max_file_size = FILE_MAX_SIZE
        check_latest_version(self._logger, self._current_version, "tofupilot")

    def _log_request(self, method: str, endpoint: str, payload: Optional[dict] = None):
        """Logs the details of the HTTP request."""
        self._logger.debug(
            f"{method} {self._base_url}{endpoint} with payload: {payload}"
        )

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Processes the response from the server and logs necessary information."""
        json_response = response.json()
        warnings: Optional[List[str]] = json_response.get("warnings")
        if warnings:
            self._log_warnings(warnings)
        message = json_response.get("message")
        if message:
            self._logger.success(message)
        return {
            "success": True,
            "message": message,
            "warnings": warnings,
            "status_code": response.status_code,
            "error": None,
        }

    def _log_warnings(self, warnings: List[str]):
        """Logs any warnings found in the response."""
        for warning in warnings:
            self._logger.warning(warning)

    def _handle_http_error(
        self, http_err: requests.exceptions.HTTPError
    ) -> Dict[str, Any]:
        """Handles HTTP errors and logs them."""
        error_message = parse_error_message(http_err.response)
        self._logger.error(error_message)
        return {
            "success": False,
            "message": None,
            "warnings": None,
            "status_code": http_err.response.status_code,
            "error": {"message": error_message},
        }

    def _handle_network_error(self, e: requests.RequestException) -> Dict[str, Any]:
        """Handles network errors and logs them."""
        self._logger.error(f"Network error: {e}")
        return {
            "success": False,
            "message": None,
            "warnings": None,
            "status_code": None,
            "error": {"message": str(e)},
        }

    def _handle_unexpected_error(self, e: Exception) -> Dict[str, Any]:
        """Handles unexpected errors and logs them."""
        error_message = f"An unexpected error occurred: {e}"
        self._logger.error(error_message)
        return {
            "success": False,
            "message": None,
            "status_code": None,
            "warnings": None,
            "error": {"message": error_message},
        }

    def create_run(
        self,
        procedure_id: str,
        unit_under_test: UnitUnderTest,
        run_passed: bool,
        steps: Optional[List[Step]] = None,
        started_at: datetime = None,
        duration: timedelta = None,
        sub_units: Optional[List[SubUnit]] = None,
        report_variables: Optional[Dict[str, str]] = None,
        attachments: Optional[List[str]] = None,
    ) -> dict:
        self._logger.info(f"Starting run creation...")

        if attachments is not None:
            validate_files(
                self._logger, attachments, self._max_attachments, self._max_file_size
            )

        payload = {
            "procedure_id": procedure_id,
            "unit_under_test": unit_under_test,
            "run_passed": run_passed,
            "client": "Python",
            "client_version": self._current_version,
        }

        if steps is not None:
            for step in steps:
                if step["duration"] is not None:
                    step["duration"] = timedelta_to_iso(step["duration"])
                if step["started_at"] is not None:
                    step["started_at"] = datetime_to_iso(step["started_at"])
            payload["steps"] = steps

        if started_at is not None:
            payload["started_at"] = datetime_to_iso(started_at)

        if duration is not None:
            payload["duration"] = timedelta_to_iso(duration)

        if sub_units is not None:
            payload["sub_units"] = sub_units

        if report_variables is not None:
            payload["report_variables"] = report_variables

        self._log_request("POST", "/runs", payload)

        try:
            response = requests.post(
                f"{self._base_url}/runs",
                json=payload,
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            result = self._handle_response(response)

            run_id = result.get("id")
            if attachments:
                handle_attachments(
                    self._logger, self._headers, self._base_url, attachments, run_id
                )

            return result

        except requests.exceptions.HTTPError as http_err:
            return self._handle_http_error(http_err)

        except requests.RequestException as e:
            return self._handle_network_error(e)

        except Exception as e:
            return self._handle_unexpected_error(e)

    def create_run_from_report(self, file_path: str, importer: str = "OPENHTF") -> dict:
        self._logger.info(f'Starting run creation from file "{file_path}"...')

        if importer not in Importer.__members__:
            error_message = f"Invalid importer '{importer}'. Must be one of: {', '.join(Importer.__members__.keys())}"
            self._logger.error(error_message)
            raise ValueError(error_message)

        importer_enum = Importer[importer]
        validate_files(
            self._logger, [file_path], self._max_attachments, self._max_file_size
        )

        upload_url, upload_id = initialize_upload(
            self._headers, self._base_url, file_path
        )
        upload_file(upload_url, file_path)

        payload = {
            "upload_id": upload_id,
            "importer": importer_enum.value,
            "client": "Python",
            "client_version": self._current_version,
        }

        self._log_request("POST", "/import", payload)

        try:
            response = requests.post(
                f"{self._base_url}/import",
                json=payload,
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            return self._handle_response(response)

        except requests.exceptions.HTTPError as http_err:
            return self._handle_http_error(http_err)

        except requests.RequestException as e:
            return self._handle_network_error(e)

        except Exception as e:
            return self._handle_unexpected_error(e)

    def get_runs(self, serial_number: str) -> dict:
        if not serial_number:
            error_message = "A 'serial_number' is required to fetch runs."
            self._logger.error(error_message)
            return {
                "status_code": None,
                "success": False,
                "message": None,
                "error": {"message": error_message},
            }

        self._logger.info(
            f"Fetching runs for unit with serial number {serial_number}..."
        )
        params = {"serial_number": serial_number}

        self._log_request("GET", "/runs", params)

        try:
            response = requests.get(
                f"{self._base_url}/runs",
                headers=self._headers,
                params=params,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            return self._handle_response(response)

        except requests.exceptions.HTTPError as http_err:
            return self._handle_http_error(http_err)

        except requests.RequestException as e:
            return self._handle_network_error(e)

        except Exception as e:
            return self._handle_unexpected_error(e)


def print_version_banner(current_version: str):
    """Prints current version of client"""
    banner = f"""
    TofuPilot Python Client {current_version}
    """
    print(banner.strip())
