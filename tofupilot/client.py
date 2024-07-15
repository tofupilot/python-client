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

            self._logger.info(f"✅ Test run created successfully: {url}")

            run_id = json_response.get('id')

            if attachments:
                handle_attachments(self._logger, self._headers, self._base_url, attachments, run_id)
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