import logging
import requests
import pkg_resources
from packaging import version
import warnings
from typing import Dict, List, Tuple, TypedDict, Optional
import json
import os
import mimetypes
from datetime import timedelta
import sys

allowed_formats = ['.csv', '.txt', '.jpeg', '.png', '.webp', '.bmp', '.svg', '.mp4', '.mpeg', '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.json', '.ppt', '.pptx', '.zip', '.rar', '.7z', '.tar', '.gz']

def timedelta_to_iso8601(td: timedelta) -> str:
    days = td.days
    seconds = td.seconds
    microseconds = td.microseconds

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    iso_duration = "P"
    if days > 0:
        iso_duration += f"{days}D"

    if hours > 0 or minutes > 0 or seconds > 0 or microseconds > 0:
        iso_duration += "T"
        if hours > 0:
            iso_duration += f"{hours}H"
        if minutes > 0:
            iso_duration += f"{minutes}M"
        if seconds > 0 or microseconds > 0:
            iso_duration += f"{seconds}"
            if microseconds > 0:
                iso_duration += f".{microseconds:06d}"
            iso_duration += "S"

    return iso_duration

class UnitUnderTest(TypedDict):
    part_number: str
    serial_number: str
    revision: Optional[str]

class SubUnit(TypedDict):
    serial_number: str

class TofuPilotClient:
    def __init__(self, api_key: str, base_url: str = "https://www.tofupilot.com"):
        self._api_key = api_key
        self._base_url = f"{base_url}/api/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
        self._logger = self._setup_logger(logging.INFO)
        self._max_attachments = 100
        self._max_file_size = 10 * 1024 * 1024 # 10 MB
        self._allowed_file_formats = allowed_formats
        self._check_latest_version('tofupilot')

    def _setup_logger(self, log_level: int):
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(handler)
        return logger

    def _check_latest_version(self, package_name: str):
        try:
            response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
            response.raise_for_status()
            latest_version = response.json()['info']['version']
            installed_version = pkg_resources.get_distribution(package_name).version
            if version.parse(installed_version) < version.parse(latest_version):
                warnings.warn(
                    f'You are using {package_name} version {installed_version}, however version {latest_version} is available. '
                    f'You should consider upgrading via the "pip install --upgrade {package_name}" command.',
                    UserWarning
                )
        except requests.RequestException as e:
            self._logger.warning(f"Error checking the latest version: {e}")
        except pkg_resources.DistributionNotFound:
            self._logger.info(f"Package {package_name} is not installed.")
        except Exception as e:
            self._logger.error(f"An unexpected error occurred: {e}")

    def _log_and_raise(self, error_message: str):
        self._logger.error(error_message)
        raise RuntimeError(error_message)

    def _parse_error_message(self, response: requests.Response) -> str:
        try:
            error_data = response.json()
            return error_data.get("error", {}).get("message", f"HTTP error occurred: {response.text}")
        except ValueError:
            return f"HTTP error occurred: {response.text}"

    def _initialize_upload(self, file_path: str) -> Tuple[str, str]:
        initialize_url = f"{self._base_url}/uploads/initialize"
        file_name = os.path.basename(file_path)
        payload = {"name": file_name}
        response = requests.post(initialize_url, data=json.dumps(payload), headers=self._headers)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get('uploadUrl'), response_json.get('id')

    def _upload_file(self, upload_url: str, file_path: str) -> bool:
        with open(file_path, 'rb') as file:
            content_type, _ = mimetypes.guess_type(file_path) or 'application/octet-stream'
            upload_response = requests.put(upload_url, data=file, headers={'Content-Type': content_type})
            return upload_response.status_code == 200

    def _notify_server(self, upload_id: str, run_id: str) -> bool:
        sync_url = f"{self._base_url}/uploads/sync"
        sync_payload = {"upload_id": upload_id, "run_id": run_id}
        sync_response = requests.post(sync_url, data=json.dumps(sync_payload), headers=self._headers)
        return sync_response.status_code == 200

    def _validate_attachments(self, attachments: List[str]):
        if len(attachments) > self._max_attachments:
            self._log_and_raise(f"Number of attachments exceeds the maximum allowed limit of {self._max_attachments}")

        for file_path in attachments:
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension not in self._allowed_file_formats:
                self._log_and_raise(f"File format not allowed: {file_extension}")
            
            file_size = os.path.getsize(file_path)
            if file_size > self._max_file_size:
                self._log_and_raise(f"File size exceeds the maximum allowed size of {self._max_file_size} bytes: {file_path}")

    def _handle_attachments(self, attachments: List[str], run_id: str):
        for file_path in attachments:
            self._logger.info(f"Uploading {file_path}...")
            try:
                upload_url, upload_id = self._initialize_upload(file_path)
                if upload_url and self._upload_file(upload_url, file_path):
                    if not self._notify_server(upload_id, run_id):
                        self._logger.error(f"Failed to notify server for file: {file_path}")
                        break
                else:
                    self._logger.error(f"Failed to upload file: {file_path}")
                    break
            except requests.RequestException as e:
                self._logger.error(f"Network error uploading file {file_path}: {e}")
                break
            except Exception as e:
                self._logger.error(f"Error uploading file {file_path}: {e}")
                break
            self._logger.info(f"✅ {file_path} uploaded")

    def create_run(self, procedure_id: str, unit_under_test: UnitUnderTest, run_passed: bool, duration: timedelta = None, sub_units: Optional[List[SubUnit]] = None, params: Optional[Dict[str, str]] = None, attachments: Optional[List[str]] = None) -> dict:
        if attachments is not None:
            self._validate_attachments(attachments=attachments)

        payload = {
            "procedure_id": procedure_id,
            "unit_under_test": unit_under_test,
            "run_passed": run_passed,
        }

        if duration is not None:
            payload["duration"] = timedelta_to_iso8601(duration)

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
            response.raise_for_status()
            json_response = response.json()
            url = json_response.get('url')

            self._logger.info(f"✅ Test run created successfully: {url}")

            run_id = json_response.get('id')

            if attachments:
                self._handle_attachments(attachments, run_id)
            return {
                "success": True,
                "message": { "url": url },
                "status_code": response.status_code,
                "error": None,
                "raw_response": response
            }
        except requests.exceptions.HTTPError as http_err:
            error_message = self._parse_error_message(http_err.response)
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