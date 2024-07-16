import logging
import requests
from datetime import timedelta
from typing import Dict, List, Optional
from .utils import allowed_formats, setup_logger, check_latest_version, validate_attachments, handle_attachments, timedelta_to_iso8601, parse_error_message
from .models import UnitUnderTest, SubUnit

class TofuPilotClient:
    def __init__(self, api_key: str, base_url: str = "https://www.tofupilot.com"):
        self._api_key = api_key
        self._base_url = f"{base_url}/api/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
        self._logger = setup_logger(logging.INFO)
        self._max_attachments = 100
        self._max_file_size = 10 * 1024 * 1024 # 10 MB
        self._allowed_file_formats = allowed_formats
        check_latest_version(self._logger, 'tofupilot')

    def create_run(self, procedure_id: str, unit_under_test: UnitUnderTest, run_passed: bool, duration: timedelta = None, sub_units: Optional[List[SubUnit]] = None, report_variables: Optional[Dict[str, str]] = None, attachments: Optional[List[str]] = None) -> dict:
        """
            Creates a test run with the specified parameters and uploads it to the TofuPilot platform.
            [See example](https://docs.tofupilot.com/1-create-your-first-test-run).

            Args:
                procedure_id (str): The unique identifier of the procedure to which the test run belongs.
                unit_under_test (UnitUnderTest): The unit being tested.
                run_passed (bool): Boolean indicating whether the test run was successful.
                duration (timedelta, optional): The duration of the test run. Default is None.
                sub_units (Optional[List[SubUnit]], optional): [A list of sub-units included in the test run](https://docs.tofupilot.com/2-create-a-run-with-sub-units). Default is None.
                report_variables (Optional[Dict[str, str]], optional): [A dictionary of key values that will replace the procedure's {{report_variables}}](https://docs.tofupilot.com/3-create-a-run-with-report-variables). Default is None.
                attachments (Optional[List[str]], optional): [A list of file paths for attachments to include with the test run](https://docs.tofupilot.com/4-create-a-run-with-attachments). Default is None.

            Returns:
                dict: A dictionary containing the following keys:
                    - success (bool): Whether the test run creation was successful.
                    - message (Optional[dict]): Contains URL if successful.
                    - status_code (Optional[int]): HTTP status code of the response.
                    - error (Optional[dict]): Error message if any.
                    - raw_response (Optional[requests.Response]): Raw response object from the API request.

            Raises:
                requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
                requests.RequestException: If a network error occurred.
                Exception: For any other exceptions that might occur.

        """
        self._logger.info("Creating run...")

        if attachments is not None:
            validate_attachments(self._logger, attachments, self._max_attachments, self._max_file_size, self._allowed_file_formats)

        payload = {
            "procedure_id": procedure_id,
            "unit_under_test": unit_under_test,
            "run_passed": run_passed,
        }

        if duration is not None:
            payload["duration"] = timedelta_to_iso8601(duration)

        if sub_units is not None:
            payload["sub_units"] = sub_units

        if report_variables is not None:
            payload["report_variables"] = report_variables

        try:
            response = requests.post(
                f"{self._base_url}/runs",
                json=payload,
                headers=self._headers
            )
            response.raise_for_status()
            json_response = response.json()
            url = json_response.get('url')

            self._logger.success(f"Test run created: {url}")

            run_id = json_response.get('id')

            try:
                if attachments:
                    handle_attachments(self._logger, self._headers, self._base_url, attachments, run_id)
            except Exception as e:
                self._logger.error(e)
                return {
                    "success": False,
                    "message": None,
                    "status_code": None,
                    "error": {"message": str(e)},
                    "raw_response": None
                }
            return {
                "success": True,
                "message": { "url": url },
                "status_code": response.status_code,
                "error": None,
                "raw_response": response
            }
        except requests.exceptions.HTTPError as http_err:
            error_message = parse_error_message(http_err.response)
            self._logger.error(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": http_err.response.status_code,
                "error": {"message": error_message},
                "raw_response": http_err.response
            }
        except requests.RequestException as e:
            self._logger.error(f"Network error: {e}")
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": str(e)},
                "raw_response": None
            }
        except Exception as e:
            error_message = f"Failed to create test run: {e}"
            self._logger.error(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": error_message},
                "raw_response": None
            }

    def __getattr__(self, name: str):
        if name != 'create_run':
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")