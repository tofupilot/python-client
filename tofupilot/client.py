import requests
import time
from datetime import timedelta
from typing import Callable, Dict

class TofuPilotClient:
    def __init__(self, api_key: str, base_url: str = "https://www.tofupilot.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {self.api_key}"
        }

    def create_test_run(self, procedure_id: str, component_id: str, component_revision: str, unit_sn: str, test_function: Callable[[], bool], params: Dict[str, str] = None) -> dict:
        start_time = time.time()
        test_result = test_function()
        end_time = time.time()
        duration_seconds = end_time - start_time

        # Convert duration to ISO 8601 format
        duration = timedelta(seconds=duration_seconds)
        iso_duration = f"P{duration.days}DT{duration.seconds // 3600}H{(duration.seconds // 60) % 60}M{duration.seconds % 60}.{duration.microseconds}S"

        # Set default params to an empty dictionary if None is provided
        if params is None:
            params = {}

        payload = {
            "procedure_id": procedure_id,
            "component_id": component_id,
            "component_revision": component_revision,
            "unit_sn": unit_sn,
            "run_passed": test_result,
            "duration": iso_duration,
            "params": params
        }

        response = requests.post(
            f"{self.base_url}/runs",
            json=payload,  # Directly pass the dictionary
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()['url']
