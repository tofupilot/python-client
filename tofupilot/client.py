"""Module for TofuPilot's Python API wrapper."""

from typing import Dict, List, Optional
import os
import sys
import logging
from datetime import datetime, timedelta
from importlib.metadata import version

import json
import requests
import certifi

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
    api_request,
    process_openhtf_attachments,
)


class TofuPilotClient:
    """Wrapper for TofuPilot's API that provides additional support for handling attachments."""

    def __init__(self, api_key: Optional[str] = None, url: Optional[str] = None):
        self._current_version = version("tofupilot")
        print_version_banner(self._current_version)
        self._logger = setup_logger(logging.INFO)

        # Configure SSL certificate validation
        self._setup_ssl_certificates()

        self._api_key = api_key or os.environ.get("TOFUPILOT_API_KEY")
        if self._api_key is None:
            error = "Please set TOFUPILOT_API_KEY environment variable. For more information on how to find or generate a valid API key, visit https://tofupilot.com/docs/user-management#api-key."
            self._logger.error(error)
            sys.exit(1)

        self._url = f"{url or os.environ.get('TOFUPILOT_URL') or ENDPOINT}/api/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        self._max_attachments = CLIENT_MAX_ATTACHMENTS
        self._max_file_size = FILE_MAX_SIZE
        check_latest_version(self._logger, self._current_version, "tofupilot")

    def _setup_ssl_certificates(self):
        """Configure SSL certificate validation using certifi if needed."""
        # Check if SSL_CERT_FILE is already set to a valid path
        cert_file = os.environ.get("SSL_CERT_FILE")
        if not cert_file or not os.path.isfile(cert_file):
            # Use certifi's certificate bundle
            certifi_path = certifi.where()
            if os.path.isfile(certifi_path):
                os.environ["SSL_CERT_FILE"] = certifi_path
                self._logger.debug(f"SSL: Using certifi path {certifi_path}")

    def _log_request(self, method: str, endpoint: str, payload: Optional[dict] = None):
        """Logs the details of the HTTP request."""
        self._logger.debug(
            "Request: %s %s%s payload=%s", method, self._url, endpoint, payload
        )

    def create_run(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        unit_under_test: UnitUnderTest,
        run_passed: bool,
        procedure_id: Optional[str] = None,
        procedure_name: Optional[str] = None,
        procedure_version: Optional[str] = None,
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
            unit_under_test (UnitUnderTest):
                The unit being tested.
            run_passed (bool):
                Boolean indicating whether the test run was successful.
            procedure_id (str, optional):
                The unique identifier of the procedure to which the test run belongs. Required if several procedures exists with the same procedure_name.
            procedure_name (str, optional):
                The name of the procedure to which the test run belongs. A new procedure will be created if none was found with this name.
            procedure_version (str, optional):
                The version of the procedure to which the test run belongs.
            started_at (datetime, optional):
                The datetime at which the test started. Default is None.
            duration (timedelta, optional):
                The duration of the test run. Default is None.
            steps (Optional[List[Step]], optional):
                [A list of steps included in the test run](https://tofupilot.com/docs/steps). Default is None.
            sub_units (Optional[List[SubUnit]], optional):
                [A list of sub-units included in the test run](https://tofupilot.com/docs/sub-units). Default is None.
            report_variables (Optional[Dict[str, str]], optional):
                [A dictionary of key values that will replace the procedure's {{report_variables}}](https://tofupilot.com/docs/report). Default is None.
            attachments (Optional[List[str]], optional):
                [A list of file paths for attachments to include with the test run](https://tofupilot.com/docs/attachments). Default is None.

        Returns:
            message (Optional[str]):
                Message containing run URL if successful.

        References:
            https://www.tofupilot.com/docs/api#create-a-run
        """
        print("")
        self._logger.info("Creating run...")

        if attachments is not None:
            validate_files(
                self._logger, attachments, self._max_attachments, self._max_file_size
            )

        payload = {
            "unit_under_test": unit_under_test,
            "run_passed": run_passed,
            "procedure_id": procedure_id,
            "procedure_name": procedure_name,
            "procedure_version": procedure_version,
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
        result = api_request(
            self._logger, "POST", f"{self._url}/runs", self._headers, data=payload
        )

        # Upload attachments if run was created successfully
        run_id = result.get("id")
        if run_id and attachments:
            # Ensure logger is active for attachment uploads
            if hasattr(self._logger, 'resume'):
                self._logger.resume()
                
            upload_attachments(
                self._logger, self._headers, self._url, attachments, run_id
            )

        return result

    def create_run_from_openhtf_report(self, file_path: str):
        """
        Creates a run on TofuPilot from an OpenHTF JSON report.

        Args:
            file_path (str):
                The path to the log file to be imported.

        Returns:
            str:
                The id of the newly created run.

        References:
            https://www.tofupilot.com/docs/api#create-a-run-from-a-file
        """
        # Upload report and create run from file_path
        run_id = self.upload_and_create_from_openhtf_report(file_path)

        # If run_id is not a string, it's an error response dictionary
        if not isinstance(run_id, str):
            self._logger.error("OpenHTF import failed")
            return run_id

        # Only continue with attachment upload if run_id is valid
        test_record = None
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                test_record = json.load(file)
        except FileNotFoundError:
            self._logger.error(f"File not found: {file_path}")
            return run_id
        except json.JSONDecodeError:
            self._logger.error(f"Invalid JSON: {file_path}")
            return run_id
        except PermissionError:
            self._logger.error(f"Permission denied: {file_path}")
            return run_id
        except Exception as e:
            self._logger.error(f"Error: {e}")
            return run_id

        # Now safely proceed with attachment upload
        if run_id and test_record and "phases" in test_record:
            # Add a visual separator after the run success message
            print("")
            self._logger.info("Processing attachments from OpenHTF test record")

            # Use the centralized function to process all attachments
            process_openhtf_attachments(
                self._logger,
                self._headers,
                self._url,
                test_record,
                run_id,
                self._max_attachments,
                self._max_file_size,
                needs_base64_decode=True,  # JSON attachments need base64 decoding
            )
        else:
            if not test_record:
                self._logger.error("Test record load failed")
            elif "phases" not in test_record:
                self._logger.error("No phases in test record")

        return run_id

    def get_runs(self, serial_number: str) -> dict:
        """
        Fetches all runs related to a specific unit from TofuPilot.

        Args:
            serial_number (str, required): The unique identifier of the unit associated with the runs.

        Returns:
            data (Optional[dict]):
                The runs data if found.
            message (Optional[str]):
                Message returned from TofuPilot API.

        References:
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

        self._logger.info("Fetching runs for: %s", serial_number)
        params = {"serial_number": serial_number}
        self._log_request("GET", "/runs", params)
        return api_request(
            self._logger, "GET", f"{self._url}/runs", self._headers, params=params
        )

    def delete_run(self, run_id: str) -> dict:
        """
        Deletes a given run.

        Args:
            run_id (str): The complete id of the run.

        Returns:
            message (Optional[str]):
                Message if the operation was successful.

        References:
            https://www.tofupilot.com/docs/api#delete-a-run
        """
        self._logger.info("Deleting run: %s", run_id)
        self._log_request("DELETE", f"/runs/{run_id}")
        return api_request(
            self._logger, "DELETE", f"{self._url}/runs/{run_id}", self._headers
        )

    def update_unit(
        self, serial_number: str, sub_units: Optional[List[SubUnit]] = None
    ) -> dict:
        """
        Updates a given unit.

        Args:
            serial_number (str):
                The serial number of the unit.
            sub_units (Optional[List[SubUnit]]):
                The list of units to be added as sub-units of unit.

        Returns:
            message (Optional[str]):
                Message if the operation was successful.

        References:
            https://www.tofupilot.com/docs/api#update-a-unit
        """
        self._logger.info("Updating unit: %s", serial_number)
        payload = {"sub_units": sub_units}
        self._log_request("PATCH", f"/units/{serial_number}", payload)
        return api_request(
            self._logger,
            "PATCH",
            f"{self._url}/units/{serial_number}",
            self._headers,
            data=payload,
        )

    def delete_unit(self, serial_number: str) -> dict:
        """
        Deletes a given unit.

        Args:
            serial_number (str):
                The serial number of the unit.

        Returns:
            message (Optional[str]):
                Message if the operation was successful.

        References:
            https://www.tofupilot.com/docs/api#delete-a-unit
        """
        self._logger.info("Deleting unit: %s", serial_number)
        self._log_request("DELETE", f"/units/{serial_number}")
        return api_request(
            self._logger, "DELETE", f"{self._url}/units/{serial_number}", self._headers
        )

    def upload_and_create_from_openhtf_report(
        self,
        file_path: str,
    ) -> str:
        """
        Takes a path to an OpenHTF JSON file report, uploads it and creates a run from it.

        Returns:
            str:
                Id of the newly created run
        """

        print("")
        self._logger.info("Importing run...")

        # Validate report
        validate_files(
            self._logger, [file_path], self._max_attachments, self._max_file_size
        )

        # Upload report
        try:
            upload_id = upload_file(self._headers, self._url, file_path)
        except requests.exceptions.HTTPError as http_err:
            error_info = handle_http_error(self._logger, http_err)
            # Error already logged by handle_http_error
            return error_info
        except requests.RequestException as e:
            error_info = handle_network_error(self._logger, e)
            # Error already logged by handle_network_error
            return error_info

        payload = {
            "upload_id": upload_id,
            "importer": "OPENHTF",
            "client": "Python",
            "client_version": self._current_version,
        }

        self._log_request("POST", "/import", payload)

        # Create run from file using unified API request handler
        result = api_request(
            self._logger, "POST", f"{self._url}/import", self._headers, data=payload
        )

        # Return only the ID if successful, otherwise return the full result
        if result.get("success", False) is not False:
            run_id = result.get("id")
            run_url = result.get("url")

            # Explicitly log success with URL if available
            if run_url:
                self._logger.success(f"Run imported successfully: {run_url}")
            elif run_id:
                self._logger.success(f"Run imported successfully with ID: {run_id}")

            return run_id
        else:
            return result

    def get_connection_credentials(self) -> dict:
        """
        Fetches credentials required to livestream test results.

        Returns:
            values:
                a dict containing the emqx server url, the topic to connect to, and the JWT token required to connect
        """
        try:
            response = requests.get(
                f"{self._url}/streaming",
                headers=self._headers,
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            response.raise_for_status()
            values = handle_response(self._logger, response)
            return values
        except requests.exceptions.HTTPError as http_err:
            handle_http_error(self._logger, http_err)
            return None
        except requests.RequestException as e:
            handle_network_error(self._logger, e)
            return None


def print_version_banner(current_version: str):
    """Prints current version of client with tofu art"""
    # Colors for the tofu art
    yellow = "\033[33m"  # Yellow for the plane
    blue = "\033[34m"  # Blue for the cap border
    reset = "\033[0m"  # Reset color

    banner = (
        f"{blue}╭{reset} {yellow}✈{reset} {blue}╮{reset}\n"
        f"[•ᴗ•] TofuPilot Python Client {current_version}\n"
        "\n"
    )

    print(banner, end="")
