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
    verify: Optional[str] = None,
) -> str:
    """Initializes an upload and stores file in it
    
    Args:
        headers (dict): Request headers including authorization
        url (str): Base API URL
        file_path (str): Path to the file to upload
        verify (Optional[str]): Path to a CA bundle file to verify the server certificate
    
    Returns:
        str: The ID of the created upload
    """
    # Upload initialization
    initialize_url = f"{url}/uploads/initialize"
    file_name = os.path.basename(file_path)
    payload = {"name": file_name}

    response = requests.post(
        initialize_url,
        data=json.dumps(payload),
        headers=headers,
        timeout=SECONDS_BEFORE_TIMEOUT,
        verify=verify,
    )

    # Check for API key errors before raising for status
    if response.status_code == 401:
        error_data = response.json()
        error_message = error_data.get("error", {}).get("message", "Authentication failed")
        # Create a proper HTTPError with the response
        http_error = requests.exceptions.HTTPError(response=response)
        http_error.response = response
        raise http_error
    
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
            verify=verify,
        )

    return upload_id


def notify_server(headers: dict, url: str, upload_id: str, run_id: str, logger=None, verify: str | None = None) -> bool:
    """Tells TP server to sync upload with newly created run"""
    sync_url = f"{url}/uploads/sync"
    sync_payload = {"upload_id": upload_id, "run_id": run_id}

    try:
        response = requests.post(
            sync_url,
            data=json.dumps(sync_payload),
            headers=headers,
            timeout=SECONDS_BEFORE_TIMEOUT,
            verify=verify,
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
    run_id: str,
    verify: str | None,
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
            verify=verify,
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
            verify=verify,
        )
        upload_response.raise_for_status()
        
        # Link attachment to run
        notify_server(headers, url, upload_id, run_id, logger)
        
        logger.success(f"Uploaded: {name}")
        return True
    except Exception as e:
        logger.error(f"Upload failed: {name} - {str(e)}")
        return False


def notify_server(
    headers: dict,
    url: str,
    upload_id: str,
    run_id: str,
    verify: Optional[str] = None,
) -> bool:
    """Tells TP server to sync upload with newly created run
    
    Args:
        headers (dict): Request headers including authorization
        url (str): Base API URL
        upload_id (str): ID of the upload to link
        run_id (str): ID of the run to link to
        verify (Optional[str]): Path to a CA bundle file to verify the server certificate
        
    Returns:
        bool: True if successful
    """
    sync_url = f"{url}/uploads/sync"
    sync_payload = {"upload_id": upload_id, "run_id": run_id}

    response = requests.post(
        sync_url,
        data=json.dumps(sync_payload),
        verify=verify,
        headers=headers,
        timeout=SECONDS_BEFORE_TIMEOUT,
    )

    return response.status_code == 200


def upload_attachments(
    logger: Logger,
    headers: dict,
    url: str,
    paths: List[str],
    run_id: str,
    verify: Optional[str] = None,
):
    """Creates one upload per file and stores them into TofuPilot
    
    Args:
        logger (Logger): Logger instance
        headers (dict): Request headers including authorization
        url (str): Base API URL
        paths (List[Dict[str, Optional[str]]]): List of file paths to upload
        run_id (str): ID of the run to link files to
        verify (Optional[str]): Path to a CA bundle file to verify the server certificate
    """
    for file_path in paths:
        logger.info(f"Uploading: {file_path}")
        
        try:
            # Open file and prepare for upload
            with open(file_path, "rb") as file:
                name = os.path.basename(file_path)
                data = file.read()
                mimetype, _ = mimetypes.guess_type(file_path) or "application/octet-stream"
                
                # Use shared upload function
                upload_attachment_data(logger, headers, url, name, data, mimetype, run_id, verify)
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
    verify: str | None = None,
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
            logger.info(f"Found {len(phases)} phases in JSON test record")
        else:
            phases = getattr(test_record, "phases", [])
            logger.info(f"Found {len(phases)} phases in object test record")
        
        # Iterate through phases and their attachments
        for i, phase in enumerate(phases):
            # Skip if we've reached attachment limit
            if attachment_count >= max_attachments:
                logger.warning(f"Attachment limit ({max_attachments}) reached")
                break
                
            # Get attachments based on record type
            if isinstance(test_record, dict):
                phase_attachments = phase.get("attachments", {})
                phase_name = phase.get("name", f"Phase {i}")
            else:
                phase_attachments = getattr(phase, "attachments", {})
                phase_name = getattr(phase, "name", f"Phase {i}")
            
            # Skip if phase has no attachments
            if not phase_attachments:
                continue
                
            logger.info(f"Processing {len(phase_attachments)} attachments in {phase_name}")
                
            # Process each attachment in the phase
            for name, attachment in phase_attachments.items():
                # Skip if we've reached attachment limit
                if attachment_count >= max_attachments:
                    break
                    
                # Log attachment details
                if isinstance(test_record, dict):
                    logger.info(f"Attachment: {name}, Type: JSON format")
                else:
                    attrs = [attr for attr in dir(attachment) if not attr.startswith('_')]
                    logger.info(f"Attachment: {name}, Type: Object, Attributes: {attrs}")
                    
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
                    
                    # Handle different attachment types in OpenHTF
                    if attachment_data is None:
                        logger.warning(f"No data in: {name}")
                        continue
                    
                    # Handle file-based attachments in different formats
                    data = None
                    
                    # Option 1: Check for direct file_path attribute
                    if hasattr(attachment, "file_path") and getattr(attachment, "file_path"):
                        try:
                            file_path = getattr(attachment, "file_path")
                            logger.info(f"Found file_path attribute: {file_path}")
                            with open(file_path, "rb") as f:
                                data = f.read()
                        except Exception as e:
                            logger.error(f"Failed to read from file_path: {str(e)}")
                    
                    # Option 2: Check for filename attribute (used in some OpenHTF versions)
                    elif hasattr(attachment, "filename") and getattr(attachment, "filename"):
                        try:
                            file_path = getattr(attachment, "filename")
                            logger.info(f"Found filename attribute: {file_path}")
                            with open(file_path, "rb") as f:
                                data = f.read()
                        except Exception as e:
                            logger.error(f"Failed to read from filename: {str(e)}")
                            
                    # Option 3: Use the data attribute directly
                    else:
                        logger.info("Using data attribute directly")
                        data = attachment_data
                        
                    # Verify we have valid data
                    if data is None:
                        logger.error(f"No valid data found for attachment: {name}")
                        continue
                    
                    # Get size from attribute or calculate it
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
                try:
                    success = upload_attachment_data(
                        logger,
                        headers,
                        url,
                        name,
                        data,
                        mimetype,
                        run_id,
                        verify
                    )
                    
                    if success:
                        logger.success(f"Successfully uploaded attachment: {name}")
                    else:
                        logger.error(f"Failed to upload attachment: {name}")
                except Exception as e:
                    logger.error(f"Exception during attachment upload: {name} - {str(e)}")
                # Continue with other attachments regardless of success/failure
    finally:
        # If we resumed the logger and it has a pause method, pause it again
        if was_resumed and hasattr(logger, 'pause'):
            logger.pause()
