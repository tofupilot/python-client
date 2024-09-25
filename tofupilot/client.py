from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta
from importlib.metadata import version
import logging

import requests

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
    setup_logger,
    timedelta_to_iso,
    datetime_to_iso,
    handle_response,
    handle_http_error,
    handle_network_error,
    handle_unexpected_error,
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
            result = handle_response(self._logger, response)

            run_id = result.get("id")
            if attachments:
                handle_attachments(
                    self._logger, self._headers, self._base_url, attachments, run_id
                )

            return result

        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)

        except requests.RequestException as e:
            return handle_network_error(self._logger, e)

        except Exception as e:
            return handle_unexpected_error(self._logger, e)

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

        try:
            upload_url, upload_id = initialize_upload(
                self._logger, self._headers, self._base_url, file_path
            )
            upload_file(self._logger, upload_url, file_path)
        except Exception as e:
            return e

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
            return handle_response(self._logger, response)

        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)

        except requests.RequestException as e:
            return handle_network_error(self._logger, e)

        except Exception as e:
            return handle_unexpected_error(self._logger, e)

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
            return handle_response(self._logger, response, with_data=True)

        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)

        except requests.RequestException as e:
            return handle_network_error(self._logger, e)

        except Exception as e:
            return handle_unexpected_error(self._logger, e)


def print_version_banner(current_version: str):
    """Prints current version of client"""
    banner = f"""
    TofuPilot Python Client {current_version}
    """
    print(banner.strip())
