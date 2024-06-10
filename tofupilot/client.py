import requests
import time
import logging
from datetime import timedelta
from typing import Callable, Dict

class TofuPilotClientError(Exception):
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

class TofuPilotClient:
    def __init__(self, api_key: str, error_callback=None):
        self.api_key = api_key
        self.base_url = "https://www.tofupilot.com/api/v1"
        self.headers = {
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {self.api_key}"
        }
        self.error_callback = error_callback or self.default_error_handler
        self.logger = logging.getLogger(__name__)

    def default_error_handler(self, error_message):
        self.logger.error(error_message)

    def _parse_error_message(self, response):
        try:
            error_data = response.json()
            if "error" in error_data and "message" in error_data["error"]:
                return f"Error: {error_data['error']['message']}"
            else:
                return f"HTTP error occurred: {response.text}"
        except ValueError:
            return f"HTTP error occurred: {response.text}"

    def create_run(self, procedure_id: str, component_id: str, unit_sn: str, test_function: Callable[[], bool], component_revision: str = None, params: Dict[str, str] = None) -> dict:
        start_time = time.time()
        test_result = test_function()
        end_time = time.time()
        duration_seconds = end_time - start_time

        # Convert duration to ISO 8601 format
        duration = timedelta(seconds=duration_seconds)
        iso_duration = f"P{duration.days}DT{duration.seconds // 3600}H{(duration.seconds // 60) % 60}M{duration.seconds % 60}.{duration.microseconds}S"

        payload = {
            "procedure_id": procedure_id,
            "component_id": component_id,
            "unit_sn": unit_sn,
            "run_passed": test_result,
            "duration": iso_duration,
        }

        # We include component_revision if it is not None
        if component_revision is not None:
            payload["component_revision"] = component_revision

        # We include params if it is not None
        if params is not None:
            payload["params"] = params

        try:
            response = requests.post(
                f"{self.base_url}/runs",
                json=payload,  # Directly pass the dictionary
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()['url']
        except requests.exceptions.HTTPError as http_err:
            error_message = self._parse_error_message(http_err.response)
            self.error_callback(error_message)
        except Exception as e:
            error_message = f"Failed to create test run: {e}"
            self.error_callback(error_message)