import logging
import os
from datetime import datetime, timedelta
from importlib.metadata import version
from typing import Dict, List, Optional

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
    parse_error_message,
    setup_logger,
    timedelta_to_iso,
    datetime_to_iso,
)


class TofuPilotClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = ENDPOINT):
        self._current_version = version("tofupilot")
        print_version_banner(self._current_version)  # Print the version banner
        self._api_key = api_key
        self._base_url = f"{base_url}/api/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        self._logger = setup_logger(logging.INFO)
        self._max_attachments = CLIENT_MAX_ATTACHMENTS
        self._max_file_size = FILE_MAX_SIZE
        check_latest_version(self._logger, self._current_version, "tofupilot")
        if api_key is None:
            api_key = os.environ.get("TOFUPILOT_API_KEY")
        if api_key is None:
            error = "Please set TOFUPILOT_API_KEY environment variable. For more information on how to find or generate a valid API key, visit https://docs.tofupilot.com/user-management#api-key."
            self._logger.error(error)
            raise Exception(error)

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
        """
        Creates a test run with the specified parameters and uploads it to the TofuPilot platform.
        [See API reference](https://docs.tofupilot.com/runs).

        Args:
            procedure_id (str): The unique identifier of the procedure to which the test run belongs.
            unit_under_test (UnitUnderTest): The unit being tested.
            run_passed (bool): Boolean indicating whether the test run was successful.
            started_at (datetime, optional): The datetime at which the test started. Default is None.
            duration (timedelta, optional): The duration of the test run. Default is None.
            steps (Optional[List[Step]], optional): [A list of steps included in the test run](https://docs.tofupilot.com/steps). Default is None.
            sub_units (Optional[List[SubUnit]], optional): [A list of sub-units included in the test run](https://docs.tofupilot.com/sub-units). Default is None.
            report_variables (Optional[Dict[str, str]], optional): [A dictionary of key values that will replace the procedure's {{report_variables}}](https://docs.tofupilot.com/report). Default is None.
            attachments (Optional[List[str]], optional): [A list of file paths for attachments to include with the test run](https://docs.tofupilot.com/attachments). Default is None.

        Returns:
            dict: A dictionary containing the following keys:
                - success (bool): Whether the test run creation was successful.
                - message (Optional[dict]): Contains URL if successful.
                - status_code (Optional[int]): HTTP status code of the response.
                - error (Optional[dict]): Error message if any.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
            requests.RequestException: If a network error occurred.
            Exception: For any other exceptions that might occur.

        """
        self._logger.info(f"Starting run creation...")

        if attachments is not None:
            validate_files(
                self._logger,
                attachments,
                self._max_attachments,
                self._max_file_size,
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

        try:
            response = requests.post(
                f"{self._base_url}/runs",
                json=payload,
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            json_response = response.json()

            warnings: Optional[List[str]] = json_response.get("warnings")
            if warnings:
                for warning in warnings:
                    self._logger.warning(warning)

            message = json_response.get("message")
            self._logger.success(message)

            run_id = json_response.get("id")

            try:
                if attachments:
                    handle_attachments(
                        self._logger, self._headers, self._base_url, attachments, run_id
                    )
            except Exception as e:
                self._logger.error(e)
                return {
                    "success": False,
                    "message": None,
                    "status_code": None,
                    "error": {"message": str(e)},
                }
            return {
                "success": True,
                "message": message,
                "status_code": response.status_code,
                "error": None,
            }
        except requests.exceptions.HTTPError as http_err:
            error_message = parse_error_message(http_err.response)
            self._logger.error(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": http_err.response.status_code,
                "error": {"message": error_message},
            }
        except requests.RequestException as e:
            self._logger.error("Network error: %s", e)
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": str(e)},
            }
        except Exception as e:
            error_message = f"Failed to create test run: {e}"
            self._logger.error(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": error_message},
            }

    def create_run_from_report(self, file_path: str, importer: str = "OPENHTF") -> dict:
        """
        Creates a run on TofuPilot from a file report (e.g. OpenHTF JSON report).

        Args:
            file_path (str): The path to the log file to be imported.
            importer (str): The type of importer to use. Defaults to "OPENHTF".

        Returns:
            dict: A dictionary containing the result of the import operation:
                - success (bool): Whether the import was successful.
                - message (Optional[str]): Message if the operation was successful.
                - status_code (Optional[int]): HTTP status code of the response.
                - error (Optional[dict]): Error message if any.

        Raises:
            ValueError: If the provided importer is not a valid Importer type.
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
            requests.RequestException: If a network error occurred.
            Exception: For any other exceptions that might occur.
        """
        self._logger.info(f'Starting run creation from file "{file_path}"...')

        # Validate the provided importer string against the Importer enum
        if importer not in Importer.__members__:
            error_message = f"Invalid importer '{importer}'. Must be one of: {', '.join(Importer.__members__.keys())}"
            self._logger.error(error_message)
            raise ValueError(error_message)

        # Convert the string to the corresponding Importer enum value
        importer_enum = Importer[importer]

        try:
            validate_files(
                self._logger,
                [file_path],
                self._max_attachments,
                self._max_file_size,
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

            response = requests.post(
                f"{self._base_url}/import",
                json=payload,
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            import_response = response.json()

            warnings: Optional[List[str]] = import_response.get("warnings")
            if warnings:
                for warning in warnings:
                    self._logger.warning(warning)

            message = import_response.get("message")
            self._logger.success(message)

            return {
                "success": True,
                "message": message,
                "status_code": response.status_code,
                "error": None,
            }

        except requests.exceptions.HTTPError as http_err:
            error_message = parse_error_message(http_err.response)
            self._logger.error(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": http_err.response.status_code,
                "error": {"message": error_message},
            }
        except requests.RequestException as e:
            self._logger.error("Network error: %s", e)
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": str(e)},
            }
        except Exception as e:
            error_message = f"Failed to import log: {e}"
            self._logger.error(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": error_message},
            }

    def get_runs(self, *args, serial_number: str = None) -> dict:
        """
        Fetches all runs related to a specific unit from TofuPilot.

        Args:
            serial_number (str, required): The unique identifier of the unit associated with the runs.

        Returns:
            dict: A dictionary containing the following keys:
                - success (bool): Whether the operation was successful.
                - message (Optional[str]): Message returned from the API.
                - data (Optional[dict]): The runs data if found.
                - status_code (Optional[int]): HTTP status code of the response.
                - error (Optional[dict]): Error message if any.

        Raises:
            ValueError: If no `serial_number` was provided.
            TypeError: If positional arguments are passed instead of keyword arguments.
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
            requests.RequestException: If a network error occurred.
            Exception: For any other exceptions that might occur.
        """
        # If any positional arguments were given
        if args:
            error_message = 'get_runs method only accepts keyword arguments. Please use `serial_number` as a named argument. For instance: client.get_runs(serial_number="YourSerialNumber")'
            self._logger.error(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": error_message},
            }

        # Checking if serial_number is provided
        if serial_number is None:
            error_message = "A 'serial_number' is required to fetch runs."
            self._logger.error(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": error_message},
            }

        # Logging fetching operation
        self._logger.info(
            f"Fetching runs for unit with serial number {serial_number}..."
        )
        params = {"serial_number": serial_number}
        endpoint = f"{self._base_url}/runs"

        try:
            response = requests.get(
                endpoint,
                headers=self._headers,
                params=params,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )

            response.raise_for_status()
            json_response = response.json()

            # Logging message from the response
            message = json_response.get("message")
            self._logger.success(message)

            # Extracting the runs data from the response
            data = json_response.get("data")

            return {
                "success": True,
                "message": message,
                "data": data,
                "status_code": response.status_code,
                "error": None,
            }

        except requests.exceptions.HTTPError as http_err:
            error_message = (
                http_err.response.json().get("error", "An HTTP error occurred.")
                if http_err.response is not None
                # Handling case where response might not have a json value
                else "An HTTP error occurred."
            )
            self._logger.error(f"HTTP error occurred: {error_message}")
            return {
                "success": False,
                "message": None,
                "status_code": (
                    http_err.response.status_code if http_err.response else None
                ),
                "error": {"message": error_message},
            }

        except requests.RequestException as e:
            self._logger.error(f"Network error: {e}")
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": str(e)},
            }

        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            self._logger.error(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": error_message},
            }


def print_version_banner(current_version: str):
    """Prints current version of client"""
    banner = f"""
    TofuPilot Python Client {current_version}
    """
    print(banner.strip())
