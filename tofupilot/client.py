import logging
import requests
import pkg_resources
from packaging import version
import warnings
import time
from datetime import timedelta
from typing import Callable, Dict, List, Tuple, Union, TypedDict, Optional
import subprocess
import sys
import io

TestFunction = Union[bool, Tuple[bool, Optional[Dict[str, str]]]]

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

    def _capture_output(self, test_function: TestFunction):
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            result = test_function()
            stdout_output = sys.stdout.getvalue()
            stderr_output = sys.stderr.getvalue()

            # Log the captured output
            if stdout_output:
                self._logger.info(stdout_output)
            if stderr_output:
                self._logger.error(stderr_output)

            if isinstance(result, list):
                # Handle subprocess if result is a list of commands
                process = subprocess.Popen(result, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()

                if stdout:
                    self._logger.info(stdout.decode())
                if stderr:
                    self._logger.error(stderr.decode())

                return process.returncode

            return result
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def create_run(self, procedure_id: str, unit_under_test: UnitUnderTest, test_function: TestFunction, sub_units: Optional[List[SubUnit]] = None) -> dict:
        start_time = time.time()
        result = self._capture_output(test_function)

        end_time = time.time()
        duration_seconds = end_time - start_time

        # Convert duration to ISO 8601 format
        duration = timedelta(seconds=duration_seconds)
        iso_duration = f"P{duration.days}DT{duration.seconds // 3600}H{(duration.seconds // 60) % 60}M{duration.seconds % 60}.{duration.microseconds}S"

        # Handle both bool and tuple return types
        if isinstance(result, tuple):
            run_passed, params = result
        else:
            run_passed = result
            params = None

        payload = {
            "procedure_id": procedure_id,
            "unit_under_test": unit_under_test,
            "run_passed": run_passed,
            "duration": iso_duration,
        }


        # We include params if it is not None
        if sub_units is not None:
            payload["sub_units"] = sub_units

        # We include params if it is not None
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
