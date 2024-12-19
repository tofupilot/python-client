"""Module for TofuPilot's Python API wrapper."""

from typing import Dict, List, Optional
import os
import sys
import logging
from datetime import datetime, timedelta
from importlib.metadata import version

import requests

from .constants import (
    ENDPOINT,
    FILE_MAX_SIZE,
    CLIENT_MAX_ATTACHMENTS,
    SECONDS_BEFORE_TIMEOUT,
)
from .models import SubUnit, UnitUnderTest, Step, Phase
from .utils import (
    check_latest_version,
    validate_files,
    upload_file,
    upload_attachments,
    setup_logger,
    timedelta_to_iso,
    datetime_to_iso,
    handle_response,
    handle_http_error,
    handle_network_error,
)


class TofuPilotClient:
    """Wrapper for TofuPilot's API that provides additional support for handling attachments."""

    def __init__(self, api_key: Optional[str] = None, url: Optional[str] = None):
        self._current_version = version("tofupilot")
        print_version_banner(self._current_version)
        self._logger = setup_logger(logging.INFO)

        self._api_key = api_key or os.environ.get("TOFUPILOT_API_KEY")
        if self._api_key is None:
            error = "Please set TOFUPILOT_API_KEY environment variable. For more information on how to find or generate a valid API key, visit https://tofupilot.com/docs/user-management#api-key."  # pylint: disable=line-too-long
            self._logger.error(error)
            sys.exit(1)

        self._url = f"{url or ENDPOINT}/api/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        self._max_attachments = CLIENT_MAX_ATTACHMENTS
        self._max_file_size = FILE_MAX_SIZE
        check_latest_version(self._logger, self._current_version, "tofupilot")

    def _log_request(self, method: str, endpoint: str, payload: Optional[dict] = None):
        """Logs the details of the HTTP request."""
        self._logger.debug(
            "%s %s%s with payload: %s", method, self._url, endpoint, payload
        )

    def create_run(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        unit_under_test: UnitUnderTest,
        run_passed: bool,
        procedure_id: Optional[str] = None,
        procedure_name: Optional[str] = None,
        steps: Optional[List[Step]] = None,
        phases: Optional[List[Phase]] = None,
        started_at: Optional[datetime] = None,
        duration: Optional[timedelta] = None,
        sub_units: Optional[List[SubUnit]] = None,
        report_variables: Optional[Dict[str, str]] = None,
        attachments: Optional[List[str]] = None,
    ) -> dict:
        """
        Creates a test run with the specified parameters and uploads it to the TofuPilot platform.

        Args:
            unit_under_test (UnitUnderTest): The unit being tested.
            run_passed (bool): Boolean indicating whether the test run was successful.
            procedure_id (str, optional): The unique identifier of the procedure to which the test run belongs. Required if several procedures exists with the same procedure_name.
            procedure_name (str, optional): The name of the procedure to which the test run belongs. A new procedure will be created if none was found with this name.
            started_at (datetime, optional): The datetime at which the test started. Default is None.
            duration (timedelta, optional): The duration of the test run. Default is None.
            steps (Optional[List[Step]], optional): [A list of steps included in the test run](https://tofupilot.com/docs/steps). Default is None.
            sub_units (Optional[List[SubUnit]], optional): [A list of sub-units included in the test run](https://tofupilot.com/docs/sub-units). Default is None.
            report_variables (Optional[Dict[str, str]], optional): [A dictionary of key values that will replace the procedure's {{report_variables}}](https://tofupilot.com/docs/report). Default is None.
            attachments (Optional[List[str]], optional): [A list of file paths for attachments to include with the test run](https://tofupilot.com/docs/attachments). Default is None.

        Returns:
            dict: A dictionary containing the following keys:
                - status_code (Optional[int]): HTTP status code of the response.
                - success (bool): Whether the test run creation was successful.
                - message (Optional[dict]): Contains URL if successful.
                - warnings (Optional[List[str]]): Warning messages if any.
                - error (Optional[dict]): Error message if any.

        References:
            For more details, see:
            https://www.tofupilot.com/docs/api#create-a-run
        """
        self._logger.info("Starting run creation...")

        if attachments is not None:
            validate_files(
                self._logger, attachments, self._max_attachments, self._max_file_size
            )

        payload = {
            "unit_under_test": unit_under_test,
            "run_passed": run_passed,
            "procedure_id": procedure_id,
            "procedure_name": procedure_name,
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

        if phases is not None:
            payload["phases"] = phases

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
                f"{self._url}/runs",
                json=payload,
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            result = handle_response(self._logger, response, additional_field="id")

            run_id = result.get("id")
            if run_id and attachments:
                upload_attachments(
                    self._logger, self._headers, self._url, attachments, run_id
                )

            return result

        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)
        except requests.RequestException as e:
            return handle_network_error(self._logger, e)

    def create_run_from_openhtf_report(
        self,
        file_path: str,
    ) -> dict:
        """
        Creates a run on TofuPilot from an OpenHTF JSON report.

        Args:
            file_path (str): The path to the log file to be imported.

        Returns:
            dict: A dictionary containing the result of the import operation:
                - status_code (Optional[int]): HTTP status code of the response.
                - success (bool): Whether the import was successful.
                - message (Optional[str]): Message if the operation was successful.
                - warnings (Optional[List[str]]): Warning messages if any.
                - error (Optional[dict]): Error message if any.

        References:
            For more details, see:
            https://www.tofupilot.com/docs/api#create-a-run-from-a-file
        """
        self._logger.info("Starting run creation...")

        # Validate report
        validate_files(
            self._logger, [file_path], self._max_attachments, self._max_file_size
        )

        # Upload report
        try:
            upload_id = upload_file(self._headers, self._url, file_path)
        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)
        except requests.RequestException as e:
            return handle_network_error(self._logger, e)

        payload = {
            "upload_id": upload_id,
            "importer": "OPENHTF",
            "client": "Python",
            "client_version": self._current_version,
        }

        self._log_request("POST", "/import", payload)

        # Create run from file
        try:
            response = requests.post(
                f"{self._url}/import",
                json=payload,
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            result = handle_response(self._logger, response, additional_field="id")

            run_id = result.get("id")

            return run_id

        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)
        except requests.RequestException as e:
            return handle_network_error(self._logger, e)

    def get_runs(self, serial_number: str) -> dict:
        """
        Fetches all runs related to a specific unit from TofuPilot.

        Args:
            serial_number (str, required): The unique identifier of the unit associated with the runs.

        Returns:
            dict: A dictionary containing the following keys:
                - status_code (Optional[int]): HTTP status code of the response.
                - success (bool): Whether the operation was successful.
                - data (Optional[dict]): The runs data if found.
                - message (Optional[str]): Message returned from the API.
                - error (Optional[dict]): Error message if any.

        Raises:
            ValueError: If no `serial_number` was provided.
            TypeError: If positional arguments are passed instead of keyword arguments.
            Exception: For any other exceptions that might occur.


        References:
            For more details, see:
            https://www.tofupilot.com/docs/api#get-runs-by-serial-number
        """
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
            "Fetching runs for unit with serial number %s...", serial_number
        )
        params = {"serial_number": serial_number}

        self._log_request("GET", "/runs", params)

        try:
            response = requests.get(
                f"{self._url}/runs",
                headers=self._headers,
                params=params,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            return handle_response(self._logger, response, additional_field="data")

        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)
        except requests.RequestException as e:
            return handle_network_error(self._logger, e)

    def delete_run(self, run_id: str) -> dict:
        """
        Deletes a given run.

        Args:
            run_id (str): The complete id of the run.

        Returns:
            dict: A dictionary describing the outcome of the deletion:
                - status_code (Optional[int]): HTTP status code of the response.
                - success (bool): Whether the import was successful.
                - message (Optional[str]): Message if the operation was successful.
                - warnings (Optional[List[str]]): Warning messages if any.
                - error (Optional[dict]): Error message if any.

        References:
            For more details, see:
            https://www.tofupilot.com/docs/api#delete-a-run
        """
        self._logger.info('Starting deletion of run "%s"...', run_id)

        self._log_request("DELETE", f"/runs/{run_id}")

        try:
            response = requests.delete(
                f"{self._url}/runs/{run_id}",
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            return handle_response(self._logger, response)

        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)
        except requests.RequestException as e:
            return handle_network_error(self._logger, e)

    def update_unit(
        self, serial_number: str, sub_units: Optional[List[SubUnit]] = None
    ) -> dict:
        """
        Updates a given unit.

        Args:
            serial_number (str): The serial number of the unit.
            sub_units (Optional[List[SubUnit]]): The list of units to be added as sub-units of unit.

        Returns:
            dict: A dictionary describing the outcome of the update:
                - status_code (Optional[int]): HTTP status code of the response.
                - success (bool): Whether the import was successful.
                - message (Optional[str]): Message if the operation was successful.
                - warnings (Optional[List[str]]): Warning messages if any.
                - error (Optional[dict]): Error message if any.

        References:
            For more details, see:
            https://www.tofupilot.com/docs/api#update-a-unit
        """
        self._logger.info('Starting update of unit "%s"...', serial_number)

        payload = {"sub_units": sub_units}

        self._log_request("PATCH", f"/units/{serial_number}", payload)

        try:
            response = requests.patch(
                f"{self._url}/units/{serial_number}",
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

    def delete_unit(self, serial_number: str) -> dict:
        """
        Deletes a given unit.

        Args:
            serial_number (str): The serial number of the unit.

        Returns:
            dict: A dictionary describing the outcome of the deletion:
                - status_code (Optional[int]): HTTP status code of the response.
                - success (bool): Whether the import was successful.
                - message (Optional[str]): Message if the operation was successful.
                - warnings (Optional[List[str]]): Warning messages if any.
                - error (Optional[dict]): Error message if any.

        References:
            For more details, see:
            https://www.tofupilot.com/docs/api#delete-a-unit
        """
        self._logger.info('Starting deletion of unit "%s"...', serial_number)

        self._log_request("DELETE", f"/units/{serial_number}")

        try:
            response = requests.delete(
                f"{self._url}/units/{serial_number}",
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            return handle_response(self._logger, response)

        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)
        except requests.RequestException as e:
            return handle_network_error(self._logger, e)

    def get_token(self) -> dict:
        """
        Fetches websocket authentication token associated with API Key.

        Returns:
            dict: A dictionary describing the outcome of the update:
                - token (str): Authentication token to connect to websocket server.
                - status_code (Optional[int]): HTTP status code of the response.
                - success (bool): Whether the import was successful.
                - message (Optional[str]): Message if the operation was successful.
                - warnings (Optional[List[str]]): Warning messages if any.
                - error (Optional[dict]): Error message if any.
        """
        self._log_request("GET", "/rooms")

        try:
            response = requests.get(
                f"{self._url}/rooms",
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            return handle_response(self._logger, response, additional_field="url")

        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(self._logger, http_err)
        except requests.RequestException as e:
            return handle_network_error(self._logger, e)


def print_version_banner(current_version: str):
    """Prints current version of client"""
    banner = f"""
    TofuPilot Python Client {current_version}
    """
    print(banner.strip())
