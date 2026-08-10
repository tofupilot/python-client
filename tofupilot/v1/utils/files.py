import json
import mimetypes
from logging import Logger
import os
from typing import List, Dict, Optional, Union
import requests
import posthog

from ..constants.requests import SECONDS_BEFORE_TIMEOUT
from .logger import LoggerStateManager
from ...error_tracking import ApiV1Error
from .network import prepare_verify_setting


def log_and_raise(logger: Logger, error_message: str):
    """Log the error and raise ApiV1Error.

    Previously called `sys.exit(1)`. That raises SystemExit, which inherits
    from BaseException, so neither the upload callback's `except Exception`
    nor OpenHTF's own handler caught it — a report over the size limit
    terminated the operator's test process rather than failing the upload.
    A library must not exit the host program; the caller decides.
    """
    error = ApiV1Error(error_message)
    posthog.capture_exception(error)
    logger.error(error_message)
    raise error


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
            exception = FileNotFoundError(
                f"The file at {file_path} does not exist or is not accessible"
            )
            posthog.capture_exception(exception)
            raise exception

        file_size = os.path.getsize(file_path)
        if file_size > max_file_size:
            log_and_raise(
                logger,
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds the maximum allowed size of {max_file_size / 1024 / 1024:.2f} MB: {file_path}",
            )


def _initialize_payload(name: str, content_type: str, size_bytes: int) -> dict:
    """Payload for `/uploads/initialize`.

    Declaring the type up front means the record carries it even if the
    post-upload metadata read is skipped. The server validates `sizeBytes`
    as positive and binds the upload grant to it exactly, so an empty or
    unknown size must omit the field (the server then issues an unsized
    grant capped at PUT time).
    """
    payload = {"name": name, "mimeType": content_type}
    if size_bytes > 0:
        payload["sizeBytes"] = size_bytes
    return payload


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
    verify_setting = prepare_verify_setting(verify)

    # Upload initialization
    initialize_url = f"{url}/uploads/initialize"
    file_name = os.path.basename(file_path)
    # `guess_type` returns (None, None) for an unknown extension, which is
    # truthy, so index before the fallback.
    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    # Read the file once and size from the buffer: sizing the path here and
    # streaming the handle at PUT would race a file still being written, and
    # the grant rejects a Content-Length that differs from the declared size.
    # `upload_attachments` already buffers whole files the same way.
    with open(file_path, "rb") as file:
        file_data = file.read()
    payload = _initialize_payload(file_name, content_type, len(file_data))

    response = requests.post(
        initialize_url,
        data=json.dumps(payload),
        headers=headers,
        timeout=SECONDS_BEFORE_TIMEOUT,
        verify=verify_setting,
    )

    # `raise_for_status` already raises an HTTPError carrying the response
    # (401 included), so callers can surface the API-key message from the
    # body without a special case here.
    response.raise_for_status()
    response_json = response.json()
    upload_url = response_json.get("uploadUrl")
    upload_id = response_json.get("id")

    if not upload_id or not upload_url:
        raise ValueError(f"Upload initialization failed: missing 'id' or 'uploadUrl' in response: {response_json}")

    # File storing — send the buffer we sized, not a re-read of the path.
    put_response = requests.put(
        upload_url,
        data=file_data,
        headers={"Content-Type": content_type},
        timeout=SECONDS_BEFORE_TIMEOUT,
        verify=verify_setting,
    )
    # The presigned URL expires 60s after `initialize`. Without this
    # check an expired or rejected upload still returned an upload_id,
    # which the caller then linked to the run — the dashboard showed
    # an attachment whose object was never stored.
    put_response.raise_for_status()

    return upload_id


def notify_server(
    headers: dict,
    url: str,
    upload_id: str,
    run_id: str,
    logger = None,
    verify: Optional[str] = None,
) -> bool:
    """Tells TP server to sync upload with newly created run
    
    Args:
        headers (dict): Request headers including authorization
        url (str): Base API URL
        upload_id (str): ID of the upload to link
        run_id (str): ID of the run to link to
        logger (Optional[Logger]): The logger to use
        verify (Optional[str]): Path to a CA bundle file to verify the server certificate
        
    Returns:
        bool: True if successful
    """
    verify_setting = prepare_verify_setting(verify)
    
    try:
        sync_url = f"{url}/uploads/sync"
        sync_payload = {"upload_id": upload_id, "run_id": run_id}

        response = requests.post(
            sync_url,
            data=json.dumps(sync_payload),
            headers=headers,
            timeout=SECONDS_BEFORE_TIMEOUT,
            verify=verify_setting,
        )
        response.raise_for_status()

        return True
    except Exception as e:
        posthog.capture_exception(e)
        # If logger is available, log the error properly
        if logger:
            with LoggerStateManager(logger):
                logger.error(f"Failed to sync attachment: {str(e)}")
        return False


def upload_attachment_data(
    logger: Logger,
    headers: dict,
    url: str,
    name: str,
    data,
    mimetype: str,
    run_id: str,
    verify: Optional[str],
) -> bool:
    """
    Uploads binary data as an attachment and links it to a run

    Uses LoggerStateManager to ensure proper logging, similar to OpenHTF implementation.
    """
    verify_setting = prepare_verify_setting(verify)
    
    try:
        initialize_url = f"{url}/uploads/initialize"
        content_type = mimetype or "application/octet-stream"
        # Encode str ourselves so the declared size counts the bytes actually
        # transmitted, not characters. For anything that isn't bytes after
        # that (streams, buffer views with multi-byte items), len() is not a
        # byte count — omit the size and take the unsized grant instead.
        if isinstance(data, str):
            data = data.encode("utf-8")
        data_size = len(data) if isinstance(data, (bytes, bytearray)) else 0
        payload = _initialize_payload(name, content_type, data_size)

        response = requests.post(
            initialize_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=SECONDS_BEFORE_TIMEOUT,
            verify=verify_setting,
        )
        response.raise_for_status()

        # Get upload details
        response_json = response.json()
        upload_url = response_json.get("uploadUrl")
        upload_id = response_json.get("id")

        # Upload the actual data
        upload_response = requests.put(
            upload_url,
            data=data,
            headers={"Content-Type": content_type},
            timeout=SECONDS_BEFORE_TIMEOUT,
            verify=verify_setting,
        )
        upload_response.raise_for_status()

        # Link attachment to run. notify_server swallows its own exceptions
        # and returns False; reporting success anyway would leave the bytes
        # stored but never linked to the run, with nothing in the log.
        if not notify_server(headers, url, upload_id, run_id, verify=verify, logger=logger):
            with LoggerStateManager(logger):
                logger.error(f"Attachment stored but not linked to run: {name}")
            return False

        # Log success with LoggerStateManager for visibility
        with LoggerStateManager(logger):
            logger.success(f"Uploaded attachment: {name}")
        return True
    except Exception as e:
        posthog.capture_exception(e)
        # Log error with LoggerStateManager for visibility
        with LoggerStateManager(logger):
            logger.error(f"Upload failed: {name} - {str(e)}")
            
            # Provide specific guidance for SSL errors with storage service
            if "storage." in str(e) and "certificate is not valid for" in str(e):
                logger.warning("Certificate must include storage subdomain")
                logger.warning("Generate wildcard certificate or add storage hostname to SAN")
        return False

def upload_attachments(
    logger: Logger,
    headers: dict,
    url: str,
    paths: List[str],
    run_id: str,
    verify: Optional[str] = None,
):
    """Creates one upload per file and stores them into TofuPilot

    Uses LoggerStateManager to ensure logging is properly handled during the upload process,
    similar to the OpenHTF implementation.s
    
    Args:
        logger (Logger): Logger instance
        headers (dict): Request headers including authorization
        url (str): Base API URL
        paths (List[Dict[str, Optional[str]]]): List of file paths to upload
        run_id (str): ID of the run to link files to
        verify (Optional[str]): Path to a CA bundle file to verify the server certificate
    """
    # Print a visual separator before attachment uploads
    print("")

    for file_path in paths:
        # Use LoggerStateManager to ensure logger is active for each file
        with LoggerStateManager(logger):
            logger.info(f"Uploading attachment: {file_path}")

        try:
            # Verify file exists
            if not os.path.exists(file_path):
                error_message = f"File not found: {file_path}"
                posthog.capture_exception(ApiV1Error(error_message))
                with LoggerStateManager(logger):
                    logger.error(error_message)
                continue

            # Open file and prepare for upload
            with open(file_path, "rb") as file:
                name = os.path.basename(file_path)
                data = file.read()
                # See the note in `upload_file`: guess_type's (None, None) is
                # truthy, so this `or` never fired and an extensionless file
                # sent Content-Type: None.
                mimetype = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

                # Use shared upload function
                upload_attachment_data(
                    logger, headers, url, name, data, mimetype, run_id, verify
                )
        except Exception as e:
            posthog.capture_exception(e)
            # Use LoggerStateManager to ensure error is visible
            with LoggerStateManager(logger):
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
    verify: Optional[str] = None,
) -> None:
    """
    Process attachments from an OpenHTF test record and upload them.

    This function centralizes the attachment processing logic used in both the
    direct TofuPilotClient.create_run_from_openhtf_report and the OpenHTF output callback.

    Uses LoggerStateManager to ensure proper logging visibility throughout the process,
    similar to the OpenHTF implementation.

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
    # Print a visual separator
    print("")

    # Use LoggerStateManager instead of directly resuming/pausing
    with LoggerStateManager(logger):
        logger.info("Processing attachments from test record")

    try:
        attachment_count = 0

        # Extract phases from test record based on type
        if isinstance(test_record, dict):
            phases = test_record.get("phases", [])
            with LoggerStateManager(logger):
                logger.info(f"Found {len(phases)} phases in JSON test record")
        else:
            phases = getattr(test_record, "phases", [])
            with LoggerStateManager(logger):
                logger.info(f"Found {len(phases)} phases in object test record")

        # Iterate through phases and their attachments
        for i, phase in enumerate(phases):
            # Skip if we've reached attachment limit
            if attachment_count >= max_attachments:
                warning_message = f"Attachment limit ({max_attachments}) reached"
                posthog.capture_exception(ApiV1Error(warning_message))
                with LoggerStateManager(logger):
                    logger.warning(warning_message)
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

            with LoggerStateManager(logger):
                logger.info(
                    f"Processing {len(phase_attachments)} attachments in {phase_name}"
                )

            # Process each attachment in the phase
            for name, attachment in phase_attachments.items():
                # Skip if we've reached attachment limit
                if attachment_count >= max_attachments:
                    break

                # Debug attachment details (using debug level to avoid cluttering the console)
                if isinstance(test_record, dict):
                    with LoggerStateManager(logger):
                        logger.debug(f"Attachment: {name}, Type: JSON format")
                else:
                    attrs = [
                        attr for attr in dir(attachment) if not attr.startswith("_")
                    ]
                    with LoggerStateManager(logger):
                        logger.debug(
                            f"Attachment: {name}, Type: Object, Attributes: {attrs}"
                        )

                # Get attachment data and size based on record type
                if isinstance(test_record, dict):
                    # Dict format (from JSON file)
                    attachment_data = attachment.get("data", "")
                    if not attachment_data:
                        with LoggerStateManager(logger):
                            logger.warning(f"No data in: {name}")
                        continue

                    try:
                        if needs_base64_decode:
                            import base64

                            data = base64.b64decode(attachment_data)
                        else:
                            data = attachment_data

                        attachment_size = len(data)
                        mimetype = attachment.get(
                            "mimetype", "application/octet-stream"
                        )
                    except Exception as e:
                        posthog.capture_exception(e)
                        with LoggerStateManager(logger):
                            logger.error(
                                f"Failed to process attachment data: {name} - {str(e)}"
                            )
                        continue
                else:
                    # Object format (from callback)
                    attachment_data = getattr(attachment, "data", None)

                    # Handle different attachment types in OpenHTF
                    if attachment_data is None:
                        warning_message = f"No data in: {name}"
                        posthog.capture_exception(ApiV1Error(warning_message))
                        with LoggerStateManager(logger):
                            logger.warning(warning_message)
                        continue

                    # Handle file-based attachments in different formats
                    data = None

                    # Option 1: Check for direct file_path attribute
                    if hasattr(attachment, "file_path") and getattr(
                        attachment, "file_path"
                    ):
                        try:
                            file_path = getattr(attachment, "file_path")
                            with LoggerStateManager(logger):
                                logger.info(f"Found file_path attribute: {file_path}")
                            with open(file_path, "rb") as f:
                                data = f.read()
                        except Exception as e:
                            posthog.capture_exception(e)
                            with LoggerStateManager(logger):
                                logger.error(f"Failed to read from file_path: {str(e)}")

                    # Option 2: Check for filename attribute (used in some OpenHTF versions)
                    elif hasattr(attachment, "filename") and getattr(
                        attachment, "filename"
                    ):
                        try:
                            file_path = getattr(attachment, "filename")
                            with LoggerStateManager(logger):
                                logger.info(f"Found filename attribute: {file_path}")
                            with open(file_path, "rb") as f:
                                data = f.read()
                        except Exception as e:
                            posthog.capture_exception(e)
                            with LoggerStateManager(logger):
                                logger.error(f"Failed to read from filename: {str(e)}")

                    # Option 3: Use the data attribute directly
                    else:
                        with LoggerStateManager(logger):
                            logger.info("Using data attribute directly")
                        data = attachment_data

                    # Verify we have valid data
                    if data is None:
                        error_message = f"No valid data found for attachment: {name}"
                        posthog.capture_exception(ApiV1Error(error_message))
                        with LoggerStateManager(logger):
                            logger.error(error_message)
                        continue

                    # Get size from attribute or calculate it
                    attachment_size = getattr(attachment, "size", len(data))
                    mimetype = getattr(
                        attachment, "mimetype", "application/octet-stream"
                    )

                # Skip oversized attachments
                if attachment_size > max_file_size:
                    warning_message = f"File too large: {name}"
                    posthog.capture_exception(ApiV1Error(warning_message))
                    with LoggerStateManager(logger):
                        logger.warning(warning_message)
                    continue

                # Increment counter and process the attachment
                attachment_count += 1

                # Use unified attachment upload function - logging is handled inside this function
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

                    # Don't log success/failure here as it's already logged in upload_attachment_data
                except Exception as e:
                    posthog.capture_exception(e)
                    with LoggerStateManager(logger):
                        logger.error(
                            f"Exception during attachment upload: {name} - {str(e)}"
                        )
                # Continue with other attachments regardless of success/failure
    except Exception as e:
        posthog.capture_exception(e)
        raise e
    finally:
        # We intentionally don't pause the logger here, as in the OpenHTF implementation
        # This allows any final log messages to be visible
        pass
