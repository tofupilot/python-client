import json
import mimetypes
from logging import Logger
import os
import sys
from typing import List, Dict, Optional
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
        file_size = os.path.getsize(file_path)
        if file_size > max_file_size:
            log_and_raise(
                logger,
                f"File size exceeds the maximum allowed size of {max_file_size} bytes: {file_path}",
            )


def upload_file(
    headers: dict,
    base_url: str,
    file_path: str,
) -> bool:
    """Initializes an upload and stores file in it"""
    # Upload initialization
    initialize_url = f"{base_url}/uploads/initialize"
    file_name = os.path.basename(file_path)
    payload = {"name": file_name}

    response = requests.post(
        initialize_url,
        data=json.dumps(payload),
        headers=headers,
        timeout=SECONDS_BEFORE_TIMEOUT,
    )

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


def notify_server(headers: dict, base_url: str, upload_id: str, run_id: str) -> bool:
    """Tells TP server to sync upload with newly created run"""
    sync_url = f"{base_url}/uploads/sync"
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
    base_url: str,
    paths: List[Dict[str, Optional[str]]],
    run_id: str,
):
    """Creates one upload per file and stores them into TofuPilot"""
    for file_path in paths:
        logger.info("Uploading %s...", file_path)

        upload_id = upload_file(headers, base_url, file_path)
        notify_server(headers, base_url, upload_id, run_id)

        logger.success(
            f"Attachment {file_path} successfully uploaded and linked to run."
        )
