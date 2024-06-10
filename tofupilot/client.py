import logging
import requests
import pkg_resources
from packaging import version
import warnings
import time
from datetime import timedelta
from typing import Callable, Dict

class TofuPilotClient:
    def __init__(self, api_key: str, error_callback=None):
        self._api_key = api_key
        self._base_url = "https://www.tofupilot.com/api/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
        self._error_callback = error_callback or self._default_error_handler
        self._logger = logging.getLogger(__name__)

        # Check for the latest version
        self._check_latest_version('tofupilot')

    @staticmethod
    def _check_latest_version(package_name):
        try:
            # Fetch the latest version from PyPI
            response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
            response.raise_for_status()
            latest_version = response.json()['info']['version']

            # Get the installed version
            installed_version = pkg_resources.get_distribution(package_name).version

            # Compare versions
            if version.parse(installed_version) < version.parse(latest_version):
                warnings.warn(
                    f'You are using {package_name} version {installed_version}, however version {latest_version} is available. '
                    f'You should consider upgrading via the "pip install --upgrade {package_name}" command.',
                    UserWarning
                )
        except requests.RequestException as e:
            print(f"Error checking the latest version: {e}")
        except pkg_resources.DistributionNotFound:
            print(f"Package {package_name} is not installed.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def _default_error_handler(self, error_message):
        self._logger.error(error_message)

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
                f"{self._base_url}/runs",
                json=payload,  # Directly pass the dictionary
                headers=self._headers
            )
            response.raise_for_status()
            url = response.json()['url']
            print(url)
            self._logger.info(url)
            return url
        except requests.exceptions.HTTPError as http_err:
            error_message = self._parse_error_message(http_err.response)
            self._error_callback(error_message)
        except Exception as e:
            error_message = f"Failed to create test run: {e}"
            self._error_callback(error_message)

    def __getattr__(self, name):
        if name != 'create_run':
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")