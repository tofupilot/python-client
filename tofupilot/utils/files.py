import json
import mimetypes
from logging import Logger
import os
import sys
from typing import List, Dict, Optional, Union
import requests

from ..constants.requests import SECONDS_BEFORE_TIMEOUT


def log_and_raise(logger: Logger, error_message: str):
    logger.error(error_message)
    sys.exit(1)


def validate_files(
    logger: Logger,
    attachments: List[str],
    max_attachments: int,
    max_file_size: int,
):
    """Validates a list of attachments by making sure they have the right size"""
    if len(attachments) > max_attachments:
        log_and_raise(
            logger,
            f"Number of attachments exceeds the maximum allowed limit of {max_attachments}",
        )

    for file_path in attachments:
        # Checking if the file exists before attempting to get its size
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"The file at {file_path} does not exist or is not accessible"
            )

        file_size = os.path.getsize(file_path)
        if file_size > max_file_size:
            log_and_raise(
                logger,
                f"File size exceeds the maximum allowed size of {max_file_size} bytes: {file_path}",
            )


def upload_file(
    logger: Logger,
    headers: dict,
    url: str,
    file_path: str,
) -> str:
    """Initializes an upload and stores file in it"""
    # Upload initialization
    initialize_url = f"{url}/uploads/initialize"
    file_name = os.path.basename(file_path)
    payload = {"name": file_name}

    try:
        response = requests.post(
            initialize_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=SECONDS_BEFORE_TIMEOUT,
        )
        
        # Check for API key errors before raising for status
        if response.status_code == 401:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Authentication failed")
            # Use the logger directly here instead of throwing an exception
            logger.error(f"API key error: {error_message}")
            raise requests.exceptions.HTTPError(response=response)
            
        response.raise_for_status()
        response_json = response.json()
        upload_url = response_json.get("uploadUrl")
        upload_id = response_json.get("id")

        # File storing
        with open(file_path, "rb") as file:
            content_type, _ = mimetypes.guess_type(file_path) or "application/octet-stream"
            requests.put(
                upload_url,
                data=file,
                headers={"Content-Type": content_type},
                timeout=SECONDS_BEFORE_TIMEOUT,
            )

        return upload_id
    except Exception as e:
        # Log exception but let it propagate for the caller to handle
        logger.error(f"Upload failed: {str(e)}")
        raise


def notify_server(headers: dict, url: str, upload_id: str, run_id: str) -> bool:
    """Tells TP server to sync upload with newly created run"""
    sync_url = f"{url}/uploads/sync"
    sync_payload = {"upload_id": upload_id, "run_id": run_id}

    response = requests.post(
        sync_url,
        data=json.dumps(sync_payload),
        headers=headers,
        timeout=SECONDS_BEFORE_TIMEOUT,
    )

    return response.status_code == 200


def upload_attachments(
    logger: Logger,
    headers: dict,
    url: str,
    paths: List[Dict[str, Optional[str]]],
    run_id: str,
):
    """Creates one upload per file and stores them into TofuPilot"""
    for file_path in paths:
        logger.info("Uploading: %s", file_path)

        upload_id = upload_file(headers, url, file_path)
        notify_server(headers, url, upload_id, run_id)

        logger.success(f"Uploaded: {file_path}")
