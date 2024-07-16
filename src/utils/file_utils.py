import os
import json
import mimetypes
import requests
from datetime import timedelta
from typing import List, Tuple

allowed_formats = ['.csv', '.txt', '.jpeg', '.png', '.webp', '.bmp', '.svg', '.mp4', '.mpeg', '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.json', '.ppt', '.pptx', '.zip', '.rar', '.7z', '.tar', '.gz']

def validate_attachments(logger, attachments: List[str], max_attachments: int, max_file_size: int, allowed_file_formats: List[str]):
    if len(attachments) > max_attachments:
        log_and_raise(logger, f"Number of attachments exceeds the maximum allowed limit of {max_attachments}")

    for file_path in attachments:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in allowed_file_formats:
            log_and_raise(logger, f"File format not allowed: {file_extension}")
        
        file_size = os.path.getsize(file_path)
        if file_size > max_file_size:
            log_and_raise(logger, f"File size exceeds the maximum allowed size of {max_file_size} bytes: {file_path}")

def initialize_upload(headers: dict, base_url: str, file_path: str) -> Tuple[str, str]:
    initialize_url = f"{base_url}/uploads/initialize"
    file_name = os.path.basename(file_path)
    payload = {"name": file_name}
    response = requests.post(initialize_url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    response_json = response.json()
    return response_json.get('uploadUrl'), response_json.get('id')

def upload_file(upload_url: str, file_path: str) -> bool:
    with open(file_path, 'rb') as file:
        content_type, _ = mimetypes.guess_type(file_path) or 'application/octet-stream'
        upload_response = requests.put(upload_url, data=file, headers={'Content-Type': content_type})
        return upload_response.status_code == 200

def notify_server(headers: dict, base_url: str, upload_id: str, run_id: str) -> bool:
    sync_url = f"{base_url}/uploads/sync"
    sync_payload = {"upload_id": upload_id, "run_id": run_id}
    sync_response = requests.post(sync_url, data=json.dumps(sync_payload), headers=headers)
    return sync_response.status_code == 200

def handle_attachments(logger, headers: dict, base_url: str, attachments: List[str], run_id: str):
    for file_path in attachments:
        logger.info(f"Uploading {file_path}...")
        try:
            upload_url, upload_id = initialize_upload(headers, base_url, file_path)
            if upload_url and upload_file(upload_url, file_path):
                if not notify_server(headers, base_url, upload_id, run_id):
                    logger.error(f"Failed to notify server for file: {file_path}")
                    break
            else:
                logger.error(f"Failed to upload file: {file_path}")
                break
        except requests.RequestException as e:
            logger.error(f"Network error uploading file {file_path}: {e}")
            break
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            break
        logger.info(f"{file_path} uploaded")

def parse_error_message(response: requests.Response) -> str:
    try:
        error_data = response.json()
        return error_data.get("error", {}).get("message", f"HTTP error occurred: {response.text}")
    except ValueError:
        return f"HTTP error occurred: {response.text}"

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

def log_and_raise(logger, error_message: str):
    logger.error(error_message)
    raise RuntimeError(error_message)