"""
Enhanced TofuPilot API client combining auto-generated OpenAPI client with production features.

This module provides the main TofuPilotClient class that extends the auto-generated client
with additional functionality from the production client including file attachments,
logging, version checking, and enhanced error handling.
"""

import logging
import os
from datetime import datetime, timedelta
from importlib.metadata import version
from typing import Optional

from .constants import (
    CLIENT_MAX_ATTACHMENTS,
    ENDPOINT,
    FILE_MAX_SIZE,
)
from .deprecated import LegacyMethods
from .openapi_client import TofuPilotClient as BaseClient
from .utils import (
    check_latest_version,
    datetime_to_iso,
    print_tofu_banner,
    process_openhtf_attachments,
    setup_logger,
    timedelta_to_iso,
    upload_attachments,
    validate_files,
)


class TofuPilotClient(BaseClient, LegacyMethods):
    """
    Enhanced TofuPilot API client.

    Combines the auto-generated OpenAPI client with production features including:
    - File attachment handling
    - Enhanced logging and error handling
    - Version checking
    - Legacy API compatibility
    - OpenHTF integration

    Args:
        api_key (str): API key for authentication with TofuPilot's API.
        base_url (str, optional): Base URL for TofuPilot's API. Defaults to production endpoint.
        verify (str, optional): Path to a CA bundle file for SSL verification.

    Example:
        client = TofuPilotClient(api_key="tp_1234567890abcdef")

        # New API (recommended)
        response = client.runs.create(body)

        # Legacy API (deprecated but still supported)
        response = client.run_create(serial_number="DEMO-001", part_number="PCB-123", ...)
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None, verify: Optional[str] = None, **kwargs):
        if base_url is None:
            base_url = os.environ.get("TOFUPILOT_URL") or ENDPOINT

        base_url = base_url.rstrip("/") + "/api"

        # Initialize the auto-generated client
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)

        # Enhanced client features from production
        self._current_version = version("tofupilot")
        print_tofu_banner(self._current_version)
        self._logger = setup_logger(logging.INFO)

        # SSL and connection settings
        self._verify = verify
        self._max_attachments = CLIENT_MAX_ATTACHMENTS
        self._max_file_size = FILE_MAX_SIZE

        # Store the full URL including /api/v1 for compatibility with tests
        self._base_url = base_url

        # Store original URL without /api/v1 for file uploads
        self._upload_base_url = base_url.replace("/api/v1", "")

        # Version checking
        check_latest_version(self._current_version, "tofupilot")

    def create_run_with_attachments(
        self,
        unit_under_test: dict[str, str],
        run_passed: bool,
        procedure_id: Optional[str] = None,
        procedure_name: Optional[str] = None,
        procedure_version: Optional[str] = None,
        steps: Optional[list[dict]] = None,
        phases: Optional[list[dict]] = None,
        started_at: Optional[datetime] = None,
        duration: Optional[timedelta] = None,
        sub_units: Optional[list[dict]] = None,
        report_variables: Optional[dict[str, str]] = None,
        attachments: Optional[list[str]] = None,
        logs: Optional[list[dict]] = None,
    ) -> dict:
        """
        Create a run with enhanced attachment support.

        This method combines the auto-generated runs.create() with production-level
        attachment handling, validation, and logging.

        Args:
            unit_under_test: The unit being tested with serial_number and part_number
            run_passed: Boolean indicating whether the test run was successful
            procedure_id: The unique identifier of the procedure
            procedure_name: The name of the procedure
            procedure_version: The version of the procedure
            steps: List of steps (deprecated, use phases instead)
            phases: List of phases with measurements
            started_at: The datetime when the test started
            duration: The duration of the test run
            sub_units: List of sub-units included in the test run
            report_variables: Dictionary of report variables
            attachments: List of file paths for attachments to include
            logs: List of log entries

        Returns:
            dict: Response from the API including run ID and URL
        """
        print("")
        self._logger.info("Creating run with attachments...")

        # Validate attachments if provided
        if attachments is not None:
            validate_files(self._logger, attachments, self._max_attachments, self._max_file_size)

        # Build the request body using auto-generated models
        from .openapi_client.models.run_create_body import RunCreateBody

        body_dict = {
            "unit_under_test": unit_under_test,
            "run_passed": run_passed,
            "client": "Python",
            "client_version": self._current_version,
        }

        # Add optional fields
        if procedure_id is not None:
            body_dict["procedure_id"] = procedure_id
        if procedure_name is not None:
            body_dict["procedure_name"] = procedure_name
        if procedure_version is not None:
            body_dict["procedure_version"] = procedure_version
        if steps is not None:
            # Process steps with datetime/duration conversion
            processed_steps = []
            for step in steps:
                step_copy = step.copy()
                if "duration" in step_copy and isinstance(step_copy["duration"], timedelta):
                    step_copy["duration"] = timedelta_to_iso(step_copy["duration"])
                if "started_at" in step_copy and isinstance(step_copy["started_at"], datetime):
                    step_copy["started_at"] = datetime_to_iso(step_copy["started_at"])
                processed_steps.append(step_copy)
            body_dict["steps"] = processed_steps
        if phases is not None:
            body_dict["phases"] = phases
        if started_at is not None:
            body_dict["started_at"] = datetime_to_iso(started_at)
        if duration is not None:
            body_dict["duration"] = timedelta_to_iso(duration)
        if sub_units is not None:
            body_dict["sub_units"] = sub_units
        if report_variables is not None:
            body_dict["report_variables"] = report_variables
        if logs is not None:
            body_dict["logs"] = logs

        # Create the run using auto-generated client
        body = RunCreateBody.from_dict(body_dict)
        result = self.runs.create(body=body)

        # Upload attachments if run was created successfully
        if hasattr(result, "id") and result.id and attachments:
            # Ensure logger is active for attachment uploads
            if hasattr(self._logger, "resume"):
                self._logger.resume()

            upload_attachments(
                self._logger,
                {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
                self._upload_base_url + "/api/v1",
                attachments,
                result.id,
                self._verify,
            )

        return result

    def create_run_from_openhtf_report(self, file_path: str) -> str:
        """
        Create a run from an OpenHTF JSON report with enhanced error handling.

        Args:
            file_path: Path to the OpenHTF JSON report file

        Returns:
            str: The ID of the newly created run
        """
        import json

        from .openapi_client.models.run_create_from_file_body import RunCreateFromFileBody

        print("")
        self._logger.info("Importing run from OpenHTF report...")

        # Validate the file
        validate_files(self._logger, [file_path], self._max_attachments, self._max_file_size)

        try:
            # Read and upload the file
            with open(file_path, "rb") as f:
                file_content = f.read()

            body = RunCreateFromFileBody(file=file_content, importer="OPENHTF")
            result = self.imports.create_from_file(body=body)

            if not hasattr(result, "id") or not result.id:
                self._logger.error("OpenHTF import failed")
                return ""

            run_id = result.id

            # Process attachments from the OpenHTF report
            try:
                with open(file_path, encoding="utf-8") as file:
                    test_record = json.load(file)

                if "phases" in test_record:
                    print("")
                    self._logger.info("Processing attachments from OpenHTF test record")

                    process_openhtf_attachments(
                        self._logger,
                        {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
                        self._upload_base_url + "/api/v1",
                        test_record,
                        run_id,
                        self._max_attachments,
                        self._max_file_size,
                        needs_base64_decode=True,
                        verify=self._verify,
                    )

            except Exception as e:
                self._logger.warning(f"Could not process attachments: {e}")

            return run_id

        except Exception as e:
            self._logger.error(f"Failed to import OpenHTF report: {e}")
            return ""


# For backward compatibility, also export the enhanced client as the main client
__all__ = ["TofuPilotClient"]
