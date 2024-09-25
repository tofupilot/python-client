import json
import mimetypes
from logging import Logger
import os
import sys
from typing import List, Tuple
import requests

from ..constants.requests import SECONDS_BEFORE_TIMEOUT
from .network import (
    handle_http_error,
    handle_network_error,
)


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


def initialize_upload(
    logger: Logger, headers: dict, base_url: str, file_path: str
) -> Tuple[str, str]:
    """Creates a new upload in TofuPilot"""
    initialize_url = f"{base_url}/uploads/initialize"
    file_name = os.path.basename(file_path)
    payload = {"name": file_name}

    try:
        response = requests.post(
            initialize_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=SECONDS_BEFORE_TIMEOUT,
        )

        response.raise_for_status()
        response_json = response.json()
        return response_json.get("uploadUrl"), response_json.get("id")

    except requests.exceptions.HTTPError as http_err:
        return handle_http_error(logger, http_err)

    except requests.RequestException as e:
        return handle_network_error(logger, e)


def upload_file(logger: Logger, upload_url: str, file_path: str) -> bool:
    """Stores a file into an upload"""
    with open(file_path, "rb") as file:
        content_type, _ = mimetypes.guess_type(file_path) or "application/octet-stream"
        try:
            upload_response = requests.put(
                upload_url,
                data=file,
                headers={"Content-Type": content_type},
                timeout=SECONDS_BEFORE_TIMEOUT,
            )
            return upload_response.status_code == 200
        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(logger, http_err)

        except requests.RequestException as e:
            return handle_network_error(logger, e)


def notify_server(
    logger: Logger, headers: dict, base_url: str, upload_id: str, run_id: str
) -> bool:
    """Tells TP server to sync upload with newly created run"""
    sync_url = f"{base_url}/uploads/sync"
    sync_payload = {"upload_id": upload_id, "run_id": run_id}
    try:
        sync_response = requests.post(
            sync_url,
            data=json.dumps(sync_payload),
            headers=headers,
            timeout=SECONDS_BEFORE_TIMEOUT,
        )
        return sync_response.status_code == 200

    except requests.exceptions.HTTPError as http_err:
        return handle_http_error(logger, http_err)

    except requests.RequestException as e:
        return handle_network_error(logger, e)


def handle_attachments(
    logger: Logger, headers: dict, base_url: str, attachments: List[str], run_id: str
):
    """Creates one upload per file and stores them into TofuPilot"""
    for file_path in attachments:
        logger.info("Uploading %s...", file_path)
        try:
            upload_url, upload_id = initialize_upload(
                logger, headers, base_url, file_path
            )
            if upload_url and upload_file(logger, upload_url, file_path):
                if not notify_server(logger, headers, base_url, upload_id, run_id):
                    logger.error(
                        f"Notification Failure: The server could not be notified of the upload for attachment '{file_path}'. The upload may not be recorded in the system. Please check the server status and retry. For more details about run attachments, visit: https://docs.tofupilot.com/attachments."
                    )
                    break
            else:
                logger.error(
                    f"Upload Failure: The attachment '{file_path}' could not be uploaded. This might be due to an inaccessible file path or an issue with the provided upload URL. Verify the file path, ensure your network connection is stable, and try again. For more detail about run attachments, visit: https://docs.tofupilot.com/attachments."
                )
                break
        except requests.exceptions.HTTPError as http_err:
            return handle_http_error(logger, http_err)

        except requests.RequestException as e:
            return handle_network_error(logger, e)

        logger.success(
            f"Attachment {file_path} successfully uploaded and linked to run."
        )
