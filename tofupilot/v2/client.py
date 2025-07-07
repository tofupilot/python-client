"""Module for TofuPilot's Python API wrapper."""

from typing import Dict, List, Optional, Union, cast, TypeVar, Type, Literal
import os
import sys
import logging
from datetime import datetime, timedelta
from importlib.metadata import version

import json
import requests
import certifi

from ..constants import (
    ENDPOINT,
    FILE_MAX_SIZE,
    CLIENT_MAX_ATTACHMENTS,
    SECONDS_BEFORE_TIMEOUT,
)
from .types import (
    SubUnit,
    UnitUnderTest,
    Step,
    Phase,
    Log,
    RunOutcome,
    CreateRunResponse,
    GetRunsResponse,
    GetUnitsResponse,
    DeleteRunResponse,
    GetRunsSortOption,
    GetUnitsSortOption,
    GetRunsExcludeField,
    GetUnitsExcludeField,
    _UpdateUnitResponse,
    _DeleteUnitResponse,
    _OpenHTFImportResult,
    _StreamingResult,
    _InitializeUploadResponse,
)
from ..utils import (
    check_latest_version,
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

T = TypeVar('T')

class TofuPilotAPIError(Exception):
    """Enhanced error with HTTP response details."""
    
    def __init__(self, message: str):
        super().__init__(message)

class Client:
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
        *,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        verify: Optional[str] = None,
    ):
        self._current_version = version("tofupilot")
        _print_version_banner(self._current_version)
        self._logger = setup_logger(logging.INFO)

        # Configure SSL certificate validation
        self._setup_ssl_certificates()

        self._api_key = api_key or os.environ.get("TOFUPILOT_API_KEY")
        if self._api_key is None:
            error = "Please set TOFUPILOT_API_KEY environment variable. For more information on how to find or generate a valid API key, visit https://tofupilot.com/docs/user-management#api-key."
            self._logger.error(error)
            sys.exit(1)

        self._url = f"{url or os.environ.get('TOFUPILOT_URL') or ENDPOINT}/api/v2"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        self._verify = verify
        self._max_attachments = CLIENT_MAX_ATTACHMENTS
        self._max_file_size = FILE_MAX_SIZE
        check_latest_version(self._logger, self._current_version, "tofupilot")

        self.runs = Runs(self)

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

    def _send(
            self,
            method: Literal["GET", "POST", "DELETE"], # TODO: Add all http methods
            endpoint: str,
            type: Type[T],
            *,
            data: Optional[Dict] = None,
            params: Optional[Dict] = None,
        ) -> T:

        url = f"{self._url}{endpoint}"
        
        self._logger.debug(
            f"V2 Request: {method=}, {url=}, {params=}, {data=}"
        )

        response = requests.request(
            method=method,
            url=url,
            json=data,
            headers=self._headers,
            params=params,
            timeout=SECONDS_BEFORE_TIMEOUT,
            verify=self._verify,
        )
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            error = handle_http_error(self._logger, http_err)
            raise TofuPilotAPIError(error["error"]["message"]) # TODO: Add more fields and make message clearer with like error codes and names
        except requests.RequestException as e:
            error = handle_network_error(self._logger, e)
            raise

        response_data = handle_response(self._logger, response)

        return cast(T, response_data)

    def _get_units(
        self,
        *,
        ids: Optional[List[str]] = None,
        serialNumbers: Optional[List[str]] = None,
        partNumbers: Optional[List[str]] = None,
        batchNumbers: Optional[List[str]] = None,
        revisionIds: Optional[List[str]] = None,
        createdFromIds: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        createdByUserId: Optional[str] = None,
        createdByStationId: Optional[str] = None,
        startTime: Optional[datetime] = None,
        endTime: Optional[datetime] = None,
        sort: Optional[GetUnitsSortOption] = None,
        exclude: Optional[List[GetUnitsExcludeField]] = None,
    ) -> GetUnitsResponse:
        """
        Fetches units from TofuPilot with various filter options.

        Args:
            ids (List[str], optional): Unit IDs to filter by.
            serialNumbers (List[str], optional): Serial numbers to filter by.
            partNumbers (List[str], optional): Part numbers to filter by.
            batchNumbers (List[str], optional): Batch numbers to filter by.
            revisionIds (List[str], optional): Revision IDs to filter by.
            createdFromIds (List[str], optional): Created from run IDs to filter by.
            limit (int, optional): Maximum number of units to return (default 50, -1 for no limit).
            offset (int, optional): Number of units to skip (for pagination).
            createdByUserId (str, optional): Filter by user ID who created the units.
            createdByStationId (str, optional): Filter by station ID that created the units.
            startTime (datetime, optional): Filter by creation time >= startTime.
            endTime (datetime, optional): Filter by creation date <= endTime.
            sort (str, optional): Sort order (-serialNumber, serialNumber, -createdAt, createdAt), default: -createdAt.
            exclude (List[str], optional): Fields to exclude from response.

        Returns:
            dict: Units data with metadata if successful.

        References:
            https://www.tofupilot.com/docs/api#get-units
        """
        self._logger.info("Fetching units with filters")
        params = {
            k: v for k, v in {
                "ids": ids,
                "serialNumbers": serialNumbers,
                "partNumbers": partNumbers,
                "batchNumbers": batchNumbers,
                "revisionIds": revisionIds,
                "createdFromIds": createdFromIds,
                "limit": limit,
                "offset": offset,
                "createdByUserId": createdByUserId,
                "createdByStationId": createdByStationId,
                "startTime": datetime_to_iso_optional(startTime),
                "endTime": datetime_to_iso_optional(endTime),
                "sort": sort,
                "exclude": exclude,
            }.items() if v is not None
        }

        return self._send(
            "GET",
            "/units",
            GetUnitsResponse,
            params=params,
        )

    def _upload_and_create_from_openhtf_report(
        self,
        file_path: str,
    ) -> _OpenHTFImportResult:
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

    def _get_connection_credentials(self) -> _StreamingResult:
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
        return self._send(
            "GET",
            "/streaming",
            _StreamingResult,
        )


def _print_version_banner(current_version: str):
    """Prints current version of client with tofu art"""
    # Colors for the tofu art
    yellow = "\033[33m"  # Yellow for the plane
    blue = "\033[34m"  # Blue for the cap border
    reset = "\033[0m"  # Reset color

    cap = f"{blue}╭{reset} {yellow}✈{reset} {blue}╮{reset}"
    tofu = "[•ᴗ•]"
    spac = "     "

    banner = (
        f"{cap } \n"
        f"{tofu} TofuPilot Python Client {current_version}\n"
        f"{spac}   Server API v2\n"
    )

    print(banner, end="")

class Runs:
    """Run-related operations"""

    def __init__(self, client: Client) -> None:
        self._client = client

    def create(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        *,
        unit_under_test: UnitUnderTest,
        run_passed: bool,
        procedure_id: Optional[str] = None,
        procedure_name: Optional[str] = None,
        procedure_version: Optional[str] = None,
        steps: Optional[List[Step]] = None,
        phases: Optional[List[Phase]] = None,
        started_at: Optional[datetime] = None,
        duration: Optional[timedelta] = None,
        ended_at: Optional[datetime] = None,
        outcome: Optional[RunOutcome] = None,
        docstring: Optional[str] = None,
        sub_units: Optional[List[SubUnit]] = None,
        attachments: Optional[List[str]] = None,
        logs: Optional[List[Log]] = None,
    ) -> CreateRunResponse:
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
            ended_at (datetime, optional):
                The datetime at which the test ended. Default is None.
            outcome (str, optional):
                The outcome of the run. One of: RUNNING, PASS, FAIL, ERROR, TIMEOUT, ABORTED. Default is None.
            docstring (str, optional):
                Documentation string for the test run. Default is None.
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
        self._client._logger.info("Creating run...")

        if attachments is not None:
            validate_files(
                self._client._logger, attachments, self._client._max_attachments, self._client._max_file_size
            )

        payload = {
            "unit_under_test": unit_under_test,
            "run_passed": run_passed,
            "procedure_id": procedure_id,
            "procedure_name": procedure_name,
            "procedure_version": procedure_version,
            "client": "Python",
            "client_version": self._client._current_version,
        }

        if steps is not None:
            for step in steps:
                if step["duration"] is not None:
                    step["duration"] = timedelta_to_iso(step["duration"])
                if step["started_at"] is not None:
                    step["started_at"] = datetime_to_iso(step["started_at"])
            payload["steps"] = steps

        if phases is not None:
            for phase in phases:
                if phase.get("start_time") is not None:
                    phase["start_time"] = datetime_to_iso(phase["start_time"])
                if phase.get("end_time") is not None:
                    phase["end_time"] = datetime_to_iso(phase["end_time"])
            payload["phases"] = phases

        if logs is not None:
            payload["logs"] = logs

        if started_at is not None:
            payload["started_at"] = datetime_to_iso(started_at)

        if duration is not None:
            payload["duration"] = timedelta_to_iso(duration)

        if ended_at is not None:
            payload["ended_at"] = datetime_to_iso(ended_at)

        if outcome is not None:
            payload["outcome"] = outcome

        if docstring is not None:
            payload["docstring"] = docstring

        if sub_units is not None:
            payload["sub_units"] = sub_units

        result = self._client._send(
            "POST",
            "/runs",
            CreateRunResponse,
            data=payload
        )

        # Upload attachments if run was created successfully
        run_id = result.get("id")
        if run_id and attachments:
            # Ensure logger is active for attachment uploads
            if hasattr(self._logger, 'resume'):
                self._client._logger.resume()
                
            upload_attachments(
                self._client._logger, self._client._headers, self._client._url, attachments, run_id, self._client._verify,
            )
        return result

    def create_from_openhtf_report(self, file_path: str) -> str:
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
        upload_res = self._client._upload_and_create_from_openhtf_report(file_path)

        if not upload_res.get("success", False):
            self._client._logger.error("OpenHTF import failed")
            return ""
        
        run_id = upload_res["run_id"]

        # Only continue with attachment upload if run_id is valid
        test_record = None
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                test_record = json.load(file)
        except FileNotFoundError:
            self._client._logger.error(f"File not found: {file_path}")
            return run_id
        except json.JSONDecodeError:
            self._client._logger.error(f"Invalid JSON: {file_path}")
            return run_id
        except PermissionError:
            self._client._logger.error(f"Permission denied: {file_path}")
            return run_id
        except Exception as e:
            self._client._logger.error(f"Error: {e}")
            return run_id

        # Now safely proceed with attachment upload
        if run_id and test_record and "phases" in test_record:
            # Add a visual separator after the run success message
            print("")
            self._client._logger.info("Processing attachments from OpenHTF test record")

            # Use the centralized function to process all attachments
            process_openhtf_attachments(
                self._client._logger,
                self._client._headers,
                self._client._url,
                test_record,
                run_id,
                self._client._max_attachments,
                self._client._max_file_size,
                needs_base64_decode=True,  # JSON attachments need base64 decoding
                verify=self._client._verify,
            )
        else:
            if not test_record:
                self._client._logger.error("Test record load failed")
            elif "phases" not in test_record:
                self._client._logger.error("No phases in test record")

        return run_id

    def get(
        self,
        *,
        ids: Optional[List[str]] = None,
        unitSerialNumbers: Optional[List[str]] = None,
        procedureIds: Optional[List[str]] = None,
        createdByUserId: Optional[str] = None,
        createdByStationId: Optional[str] = None,
        outcome: Optional[RunOutcome] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[GetRunsSortOption] = None,
        exclude: Optional[List[GetRunsExcludeField]] = None,
    ) -> GetRunsResponse:
        """
        Fetches runs from TofuPilot with various filter options.

        Args:
            ids (List[str], optional): Run IDs to filter by.
            unitSerialNumbers (List[str], optional): Unit serial numbers to filter by.
            procedureIds (List[str], optional): Procedure IDs to filter by.
            createdByUserId (str, optional): Filter by user ID who created the runs.
            createdByStationId (str, optional): Filter by station ID that created the runs.
            outcome (str, optional): Filter by run outcome (RUNNING, PASS, FAIL, ERROR, TIMEOUT, ABORTED).
            start_time (datetime, optional): Filter by start time.
            end_time (datetime, optional): Filter by end time.
            limit (int, optional): Maximum number of runs to return (default 50, -1 for no limit).
            offset (int, optional): Number of runs to skip for pagination (default 0).
            sort (str, optional): Sort order (-startedAt, startedAt, -createdAt, createdAt, -duration, duration).
            exclude (List[str], optional): Fields to exclude from response.

        Returns:
            dict: Runs data with metadata if successful.

        References:
            https://www.tofupilot.com/docs/api#get-runs
        """
        self._client._logger.info("Fetching runs with filters")
        params = {
            k: v for k, v in {
                "ids": ids,
                "unitSerialNumbers": unitSerialNumbers,
                "procedureIds": procedureIds,
                "createdByUserId": createdByUserId,
                "createdByStationId": createdByStationId,
                "outcome": outcome,
                "startTime": datetime_to_iso_optional(start_time),
                "endTime": datetime_to_iso_optional(end_time),
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "exclude": exclude,
            }.items() if v is not None
        }
        return self._client._send(
            "GET",
            "/runs",
            GetRunsResponse,
            params=params,
        )

    def delete(self, *, ids: List[str]) -> DeleteRunResponse:
        """
        Deletes multiple runs by their IDs.

        Args:
            ids (List[str]): List of run IDs to delete.

        Returns:
            dict: Success response if the operation was successful.

        References:
            https://www.tofupilot.com/docs/api#delete-runs
        """
        self._client._logger.info("Deleting %d runs", len(ids))
        params = {"ids": ids}
        return self._client._send(
            "DELETE",
            "/runs",
            DeleteRunResponse,
            params=params,
        )
