import logging
import requests
import pkg_resources
from packaging import version
import warnings
from typing import Dict, List, TypedDict, Optional

class UnitUnderTest(TypedDict):
    part_number: str
    serial_number: str
    revision: Optional[str]

class SubUnit(TypedDict):
    serial_number: str

class TofuPilotClient:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://www.tofupilot.com/api/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

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

    def _error_callback(self, error_message):
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

    def create_run(self, procedure_id: str, unit_under_test: UnitUnderTest, duration: str, run_passed: bool, sub_units: Optional[List[SubUnit]] = None, params: Optional[Dict[str, str]] = None) -> dict:
        payload = {
            "procedure_id": procedure_id,
            "unit_under_test": unit_under_test,
            "run_passed": run_passed,
            "duration": duration,
        }

        if sub_units is not None:
            payload["sub_units"] = sub_units

        if params is not None:
            payload["params"] = params

        try:
            response = requests.post(
                f"{self._base_url}/runs",
                json=payload,
                headers=self._headers
            )
            response.raise_for_status()  # Will raise an HTTPError for bad responses
            json_response = response.json()
            print("✅ Test run created successfully:", json_response["url"])
            return {
                "success": True,
                "message": json_response,
                "status_code": response.status_code,
                "error": None,
                "raw_response": response
            }
        except requests.exceptions.HTTPError as http_err:
            error_message = self._parse_error_message(http_err.response)
            self._error_callback(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": http_err.response.status_code,
                "error": {"message": error_message},
                "raw_response": http_err.response
            }
        except Exception as e:
            error_message = f"Failed to create test run: {e}"
            self._error_callback(error_message)
            return {
                "success": False,
                "message": None,
                "status_code": None,
                "error": {"message": error_message},
                "raw_response": None
            }

    def __getattr__(self, name):
        if name != 'create_run':
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")