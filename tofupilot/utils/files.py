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
    headers: dict,
    url: str,
    file_path: str,
) -> str:
    """Initializes an upload and stores file in it"""
    # Upload initialization
    initialize_url = f"{url}/uploads/initialize"
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


def notify_server(headers: dict, url: str, upload_id: str, run_id: str, logger=None) -> bool:
    """Tells TP server to sync upload with newly created run"""
    sync_url = f"{url}/uploads/sync"
    sync_payload = {"upload_id": upload_id, "run_id": run_id}

    try:
        response = requests.post(
            sync_url,
            data=json.dumps(sync_payload),
            headers=headers,
            timeout=SECONDS_BEFORE_TIMEOUT,
        )
        response.raise_for_status()
        return True
    except Exception as e:
        # If logger is available, log the error properly
        if logger:
            logger.error(str(e))
        return False


def upload_attachment_data(
    logger: Logger,
    headers: dict,
    url: str,
    name: str,
    data,
    mimetype: str,
    run_id: str
) -> bool:
    """Uploads binary data as an attachment and links it to a run"""
    try:
        # Initialize upload
        logger.info(f"Uploading: {name}")
        initialize_url = f"{url}/uploads/initialize"
        payload = {"name": name}
        
        response = requests.post(
            initialize_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=SECONDS_BEFORE_TIMEOUT,
        )
        response.raise_for_status()
        
        # Get upload details
        response_json = response.json()
        upload_url = response_json.get("uploadUrl")
        upload_id = response_json.get("id")
        
        # Upload the actual data
        content_type = mimetype or "application/octet-stream"
        upload_response = requests.put(
            upload_url,
            data=data,
            headers={"Content-Type": content_type},
            timeout=SECONDS_BEFORE_TIMEOUT,
        )
        upload_response.raise_for_status()
        
        # Link attachment to run
        notify_server(headers, url, upload_id, run_id, logger)
        
        logger.success(f"Uploaded: {name}")
        return True
    except Exception as e:
        logger.error(f"Upload failed: {name} - {str(e)}")
        return False


def upload_attachments(
    logger: Logger,
    headers: dict,
    url: str,
    paths: List[str],
    run_id: str,
):
    """Creates one upload per file path and stores them into TofuPilot"""
    for file_path in paths:
        logger.info(f"Uploading: {file_path}")
        
        try:
            # Open file and prepare for upload
            with open(file_path, "rb") as file:
                name = os.path.basename(file_path)
                data = file.read()
                content_type, _ = mimetypes.guess_type(file_path) or "application/octet-stream"
                
                # Use shared upload function
                upload_attachment_data(logger, headers, url, name, data, content_type, run_id)
        except Exception as e:
            logger.error(f"Upload failed: {file_path} - {str(e)}")
            continue
            
            
def process_openhtf_attachments(
    logger: Logger,
    headers: dict,
    url: str,
    test_record: Union[Dict, object],
    run_id: str,
    max_attachments: int,
    max_file_size: int,
    needs_base64_decode: bool = True,
) -> None:
    """
    Process attachments from an OpenHTF test record and upload them.
    
    This function centralizes the attachment processing logic used in both the 
    direct TofuPilotClient.create_run_from_openhtf_report and the OpenHTF output callback.
    
    Args:
        logger: Logger for output messages
        headers: HTTP headers for API authentication
        url: Base API URL
        test_record: OpenHTF test record (either as dict or object)
        run_id: ID of the run to attach files to
        max_attachments: Maximum number of attachments to process
        max_file_size: Maximum size per attachment
        needs_base64_decode: Whether attachment data is base64 encoded (true for dict format)
    """
    # Resume logger if it was paused
    was_resumed = False
    if hasattr(logger, 'resume'):
        logger.resume()
        was_resumed = True
    
    try:
        logger.info("Processing attachments")
        attachment_count = 0
        
        # Extract phases from test record based on type
        if isinstance(test_record, dict):
            phases = test_record.get("phases", [])
        else:
            phases = getattr(test_record, "phases", [])
        
        # Iterate through phases and their attachments
        for phase in phases:
            # Skip if we've reached attachment limit
            if attachment_count >= max_attachments:
                logger.warning(f"Attachment limit ({max_attachments}) reached")
                break
                
            # Get attachments based on record type
            if isinstance(test_record, dict):
                phase_attachments = phase.get("attachments", {})
            else:
                phase_attachments = getattr(phase, "attachments", {})
                
            # Skip if phase has no attachments
            if not phase_attachments:
                continue
                
            # Process each attachment in the phase
            for name, attachment in phase_attachments.items():
                # Skip if we've reached attachment limit
                if attachment_count >= max_attachments:
                    break
                    
                # Get attachment data and size based on record type
                if isinstance(test_record, dict):
                    # Dict format (from JSON file)
                    attachment_data = attachment.get("data", "")
                    if not attachment_data:
                        logger.warning(f"No data in: {name}")
                        continue
                        
                    try:
                        if needs_base64_decode:
                            import base64
                            data = base64.b64decode(attachment_data)
                        else:
                            data = attachment_data
                            
                        attachment_size = len(data)
                        mimetype = attachment.get("mimetype", "application/octet-stream")
                    except Exception as e:
                        logger.error(f"Failed to process attachment data: {name} - {str(e)}")
                        continue
                else:
                    # Object format (from callback)
                    attachment_data = getattr(attachment, "data", None)
                    if attachment_data is None:
                        logger.warning(f"No data in: {name}")
                        continue
                        
                    data = attachment_data
                    attachment_size = getattr(attachment, "size", len(data))
                    mimetype = getattr(attachment, "mimetype", "application/octet-stream")
                
                # Skip oversized attachments
                if attachment_size > max_file_size:
                    logger.warning(f"File too large: {name}")
                    continue
                    
                # Increment counter and process the attachment
                attachment_count += 1
                logger.info(f"Uploading: {name}")
                
                # Use unified attachment upload function
                upload_attachment_data(
                    logger,
                    headers,
                    url,
                    name,
                    data,
                    mimetype,
                    run_id
                )
                # Continue with other attachments regardless of success/failure
    finally:
        # If we resumed the logger and it has a pause method, pause it again
        if was_resumed and hasattr(logger, 'pause'):
            logger.pause()