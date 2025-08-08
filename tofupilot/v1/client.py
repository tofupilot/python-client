"""Module for TofuPilot's Python API wrapper."""

from typing import Dict, List, Optional, Union, cast
import os
import sys
import logging
from datetime import datetime, timedelta
from importlib.metadata import version

import json
import requests
import certifi

import posthog
from ..error_tracking import ApiV1Error
from .constants import (
    ENDPOINT,
    FILE_MAX_SIZE,
    CLIENT_MAX_ATTACHMENTS,
)
from .models import SubUnit, UnitUnderTest, Step, Phase, Log, RunOutcome
from .responses import (
    CreateRunResponse,
    GetRunsResponse,
    _OpenHTFImportResult,
    _StreamingResult,
    _StreamingCredentials,
    _InitializeUploadResponse,
    ErrorResponse,
)
from .utils import (
    validate_files,
    upload_file,
    upload_attachments,
    setup_logger,
    timedelta_to_iso,
    datetime_to_iso,
    datetime_to_iso_optional,
    handle_response,
    handle_http_error,
    handle_network_error,
    api_request,
    process_openhtf_attachments,
)
from ..banner import print_banner_and_check_version

from .utils import api_request


class TofuPilotClient:
    """Wrapper for TofuPilot's API that provides additional support for handling attachments.
    
    Args:
        api_key (Optional[str]): API key for authentication with TofuPilot's API.
            If not provided, the TOFUPILOT_API_KEY environment variable will be used.
        url (Optional[str]): Base URL for TofuPilot's API.
            If not provided, the TOFUPILOT_URL environment variable or the default endpoint will be used.
        verify (Optional[str]): Path to a CA bundle file to verify TofuPilot's server certificate.
            Useful for connecting to instances with custom/self-signed certificates.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        verify: Optional[str] = None,
    ):
        self._logger = setup_logger(logging.INFO)
        self._current_version = print_banner_and_check_version()

        # Configure SSL certificate validation
        self._setup_ssl_certificates()

        self._api_key = api_key or os.environ.get("TOFUPILOT_API_KEY")
        if self._api_key is None:
            error = "Please set TOFUPILOT_API_KEY environment variable. For more information on how to find or generate a valid API key, visit https://tofupilot.com/docs/user-management#api-key."
            posthog.capture_exception(ApiV1Error(error))
            self._logger.error(error)
            sys.exit(1)

        if url:
            self._url = f"{url}/api/v1"
        else:
            tofupilot_url = os.environ.get('TOFUPILOT_URL', ENDPOINT)
            self._url = f"{tofupilot_url}/api/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        self._verify = verify
        self._max_attachments = CLIENT_MAX_ATTACHMENTS
        self._max_file_size = FILE_MAX_SIZE

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
        attachments: Optional[List[str]] = None,
        logs: Optional[List[Log]] = None,
    ) -> Union[CreateRunResponse, ErrorResponse]:
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
                [A list of steps included in the test run](https://tofupilot.com/docs/steps). DEPRECATED: Use phases and measurements instead. Default is None.
            phases (Optional[List[Phase]], optional):
                [A list of phases included in the test run](https://tofupilot.com/docs/phases). Default is None.
            sub_units (Optional[List[SubUnit]], optional):
                [A list of sub-units included in the test run](https://tofupilot.com/docs/sub-units). Default is None.
            attachments (Optional[List[str]], optional):
                [A list of file paths for attachments to include with the test run](https://tofupilot.com/docs/attachments). Default is None.
            logs (Optional[List[Log]], optional):
                [A list of log entries for the test run](https://tofupilot.com/docs/logs). Default is None.

        Returns:
            CreateRunResponse:
                Dict containing run id if successful.

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

        if logs is not None:
            payload["logs"] = logs

        if started_at is not None:
            payload["started_at"] = datetime_to_iso(started_at)

        if duration is not None:
            payload["duration"] = timedelta_to_iso(duration)

        if sub_units is not None:
            payload["sub_units"] = sub_units

        self._log_request("POST", "/runs", payload)
        result = cast(
            Union[CreateRunResponse, ErrorResponse],
            api_request(
                self._logger,
                "POST",
                f"{self._url}/runs",
                self._headers,
                data=payload,
                verify=self._verify,
            )
        )
        result["success"] = result.get("success", True) # pyright: ignore[reportGeneralTypeIssues]

        # Upload attachments if run was created successfully
        run_id = result.get("id")
        if run_id and attachments:
            # Ensure logger is active for attachment uploads
            if hasattr(self._logger, 'resume'):
                self._logger.resume()
                
            upload_attachments(
                self._logger, self._headers, self._url, attachments, run_id, self._verify,
            )
        return result

    def create_run_from_openhtf_report(self, file_path: str) -> str:
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
        upload_res = self._upload_and_create_from_openhtf_report(file_path)

        if not upload_res.get("success", False):
            error = "OpenHTF import failed"
            posthog.capture_exception(ApiV1Error(error))
            self._logger.error(error)
            return ""
        
        run_id = upload_res["run_id"]

        # Only continue with attachment upload if run_id is valid
        test_record = None
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                test_record = json.load(file)
        except FileNotFoundError as e:
            posthog.capture_exception(e)
            self._logger.error(f"File not found: {file_path}")
            return run_id
        except json.JSONDecodeError as e:
            posthog.capture_exception(e)
            self._logger.error(f"Invalid JSON: {file_path}")
            return run_id
        except PermissionError as e:
            posthog.capture_exception(e)
            self._logger.error(f"Permission denied: {file_path}")
            return run_id
        except Exception as e:
            posthog.capture_exception(e)
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
                verify=self._verify,
            )
        else:
            if not test_record:
                self._logger.error("Test record load failed")
            elif "phases" not in test_record:
                self._logger.error("No phases in test record")

        return run_id
    
    def get_runs(self, serial_number: str) -> Union[GetRunsResponse, ErrorResponse]:
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
            posthog.capture_exception(ApiV1Error(error_message))
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
        result =  cast(
            Union[GetRunsResponse, ErrorResponse],
            api_request(
                self._logger,
                "GET",
                f"{self._url}/runs",
                self._headers,
                params=params,
                verify=self._verify,
            )
        )
        result["success"] = result.get("success", True) # pyright: ignore[reportGeneralTypeIssues]

        return result

    def _upload_and_create_from_openhtf_report(
        self,
        file_path: str,
    ) -> Union[_OpenHTFImportResult, ErrorResponse]:
        """
        Takes a path to an OpenHTF JSON file report, uploads it and creates a run from it.

        Returns:
            Dict
        """

        print("")
        self._logger.info("Importing run...")

        # Validate report
        validate_files(
            self._logger, [file_path], self._max_attachments, self._max_file_size
        )

        # Upload report
        try:
            # First, check if we have a valid API key directly (avoids cryptic errors)
            if not self._api_key or len(self._api_key) < 10:
                self._logger.error("API key error: Invalid API key format.")
                return {"success": False, "error": {"message": "Invalid API key format."}}
            
            upload_id = upload_file(self._headers, self._url, file_path, self._verify)
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
            self._logger,
            "POST",
            f"{self._url}/import",
            self._headers,
            data=payload,
            verify=self._verify,
        )

         # Return only the ID if successful, otherwise return the full result
        if result.get("success", True) is not False:
            run_id = result.get("id")
            run_url = result.get("url")

            # Explicitly log success with URL if available
            if run_url:
                self._logger.success(f"Run imported successfully: {run_url}")
            elif run_id:
                self._logger.success(f"Run imported successfully with ID: {run_id}")

            return {
                "success": True,
                "run_id": run_id,
                "upload_id": upload_id,
            }
        else:
            return {**result, "upload_id": upload_id,}

    def _get_connection_credentials(self) -> Union[_StreamingResult, ErrorResponse]:
        """
        Fetches credentials required to livestream test results.

        Returns:
            a dict containing
                "success":
                    a bool indicating success
                "values" if success:
                    a dict containing:
                        - token: JWT used for authentication
                        - operatorPage: URL to the operator page
                        - clientOptions: options for paho.mqtt.Client
                        - willOptions: options for paho.mqtt.Client.will_set
                        - connectOptions: options for paho.mqtt.Client.connect (host, port, keepalive)
                        - publishOptions: options for paho.mqtt.Client.publish (topic, retain, qos)
                        - subscribeOptions: options for paho.mqtt.Client.subscribe (topic, qos)
                other fields as set in handle_http_error and handle_network_error
        """
        self._log_request("GET", "/streaming")
        
        result = api_request(
            self._logger,
            "GET",
            f"{self._url}/streaming",
            self._headers,
            verify=self._verify,
        )
        if result.get("success", True):
            return {"success": True, "values": cast(_StreamingCredentials, result)}
        else:
            return cast(ErrorResponse, result)
