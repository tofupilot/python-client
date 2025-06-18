import os
import json
import datetime
import tempfile
from typing import Optional

from openhtf.core.test_record import TestRecord
from openhtf.output.callbacks import json_factory
import requests

from .. import TofuPilotClient
from ..constants import SECONDS_BEFORE_TIMEOUT
from ..utils import (
    notify_server,
)
from ..utils.logger import LoggerStateManager


class upload:  # pylint: disable=invalid-name
    """
    OpenHTF output callback to automatically upload the test report to TofuPilot upon test completion.

    This function behaves similarly to manually parsing the OpenHTF JSON test report and calling
    `TofuPilotClient().create_run()` with the parsed data.

    Args:
        api_key (Optional[str]): API key for authentication with TofuPilot's API.
        allow_nan (Optional[bool]): Whether to allow NaN values in JSON serialization.
        url (Optional[str]): Base URL for TofuPilot's API.
        client (Optional[TofuPilotClient]): An existing TofuPilot client instance to use.
        verify (Optional[str]): Path to a CA bundle file to verify TofuPilot's server certificate.
            Useful for connecting to instances with custom/self-signed certificates.

    ### Usage Example:

    ```python
    from openhtf import test
    from tofupilot.openhtf import upload

    # ...

    def main():
        test = Test(*your_phases, procedure_id="FVT1")

        # Add TofuPilot's upload callback to automatically send the test report upon completion
        test.add_output_callback(upload())

        test.execute(lambda: "SN15")
    ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        allow_nan: Optional[bool] = False,
        url: Optional[str] = None,
        client: Optional[TofuPilotClient] = None,
        verify: Optional[str] = None,
    ):
        self.allow_nan = allow_nan
        self.client = client or TofuPilotClient(api_key=api_key, url=url, verify=verify)
        self._logger = self.client._logger
        self._url = self.client._url
        self._headers = self.client._headers
        self._verify = verify  # Kept for backward compatibility
        self._max_attachments = self.client._max_attachments
        self._max_file_size = self.client._max_file_size

    def __call__(self, test_record: TestRecord) -> str:
        """
        Returns:
            str:
                Id of the initial upload
                (This id is present in the ApiCall table of the database)
        """
        # Resume logger to ensure it's active during attachment processing
        was_logger_resumed = False
        if hasattr(self._logger, "resume"):
            self._logger.resume()
            was_logger_resumed = True

        try:
            # Extract relevant details from the test record
            dut_id = test_record.dut_id
            test_name = test_record.metadata.get("test_name")

            # Convert milliseconds to a datetime object
            start_time = datetime.datetime.fromtimestamp(
                test_record.start_time_millis / 1000.0
            )

            # Format the timestamp as YYYY-MM-DD_HH_MM_SS_SSS
            start_time_formatted = start_time.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

            temp_dir = tempfile.gettempdir()

            # Craft system-agnostic temporary filename
            filename = os.path.join(
                temp_dir, f"{dut_id}.{test_name}.{start_time_formatted}.json"
            )

            # Use the existing OutputToJSON callback to write to the custom file
            output_callback = json_factory.OutputToJSON(
                filename,
                inline_attachments=False,  # Exclude raw attachments
                allow_nan=self.allow_nan,
                indent=4,
            )

            # Open the custom file and write serialized test record to it
            with open(filename, "w", encoding="utf-8") as file:
                for json_line in output_callback.serialize_test_record(test_record):
                    file.write(json_line)

            try:
                # Use auto-generated imports API for creating run from file
                from ..openapi_client.models.run_create_from_file_body import RunCreateFromFileBody
                
                # Read the file content as bytes
                with open(filename, 'rb') as f:
                    file_content = f.read()
                
                # Create the body using auto-generated model
                body = RunCreateFromFileBody(file=file_content, importer="OPENHTF")
                
                # Use the new auto-generated API
                result = self.client.imports.create_from_file(body=body)
                
                # Handle response - the auto-generated API returns the model directly
                run_id = None
                original_upload_id = None
                
                if hasattr(result, 'id') and result.id:
                    run_id = result.id
                    # For upload_id, we'll generate a placeholder since the new API structure is different
                    original_upload_id = f"openhtf_{run_id}"
                    
                    # Log success
                    if hasattr(result, 'url') and result.url:
                        self._logger.success(f"Run imported successfully: {result.url}")
                    else:
                        self._logger.success(f"Run imported successfully with ID: {run_id}")
                else:
                    self._logger.error("Run creation failed, skipping attachments")
                    return ""

            except Exception as e:
                self._logger.error(f"Error creating run: {str(e)}")
                return ""
            finally:
                # Ensure the file is deleted after processing
                if os.path.exists(filename):
                    os.remove(filename)

            # Process attachments
            number_of_attachments = 0
            for phase_idx, phase in enumerate(test_record.phases):
                # Count attachments silently
                attachment_count = len(phase.attachments)

                # Keep only max number of attachments
                if number_of_attachments >= self._max_attachments:
                    self._logger.warning(
                        f"Attachment limit ({self._max_attachments}) reached"
                    )
                    break

                # Process each attachment in the phase
                for attachment_name, attachment in phase.attachments.items():
                    # Remove attachments that exceed the max file size
                    if attachment.size > self._max_file_size:
                        self._logger.warning(f"File too large: {attachment_name}")
                        continue
                    if number_of_attachments >= self._max_attachments:
                        break

                    number_of_attachments += 1

                    # Use LoggerStateManager to temporarily activate the logger
                    with LoggerStateManager(self._logger):
                        self._logger.info(f"Uploading attachment...")

                    # Use auto-generated uploads API for initialization
                    from ..openapi_client.models.upload_initialize_body import UploadInitializeBody
                    
                    try:
                        # Initialize upload using auto-generated API
                        init_body = UploadInitializeBody(name=attachment_name)
                        init_response = self.client.uploads.initialize(body=init_body)
                        
                        # Extract upload URL and ID from auto-generated response
                        if hasattr(init_response, 'upload_url') and hasattr(init_response, 'id'):
                            upload_url = init_response.upload_url
                            upload_id = init_response.id
                        else:
                            # Fallback to dict-style access if needed
                            upload_url = getattr(init_response, 'upload_url', None)
                            upload_id = getattr(init_response, 'id', None)
                            
                        if not upload_url or not upload_id:
                            self._logger.error("Failed to get upload URL or ID from initialization")
                            continue

                        # Handle file attachments created with test.attach_from_file
                        try:
                            attachment_data = attachment.data

                            # Some OpenHTF implementations have file path in the attachment object
                            if hasattr(attachment, "file_path") and getattr(
                                attachment, "file_path"
                            ):
                                try:
                                    with open(
                                        getattr(attachment, "file_path"), "rb"
                                    ) as f:
                                        attachment_data = f.read()
                                        self._logger.info(
                                            f"Read file data from {attachment.file_path}"
                                        )
                                except Exception as e:
                                    self._logger.warning(
                                        f"Could not read from file_path: {str(e)}"
                                    )
                                    # Continue with attachment.data

                            requests.put(
                                upload_url,
                                data=attachment_data,
                                headers={"Content-Type": attachment.mimetype},
                                timeout=SECONDS_BEFORE_TIMEOUT,
                            )
                        except Exception as e:
                            self._logger.error(f"Error uploading data: {str(e)}")
                            continue

                        # Use auto-generated uploads sync API instead of notify_server
                        from ..openapi_client.models.upload_sync_upload_body import UploadSyncUploadBody
                        
                        try:
                            # Sync the upload using auto-generated API
                            sync_body = UploadSyncUploadBody(
                                upload_id=upload_id,
                                run_id=run_id
                            )
                            sync_response = self.client.uploads.sync(body=sync_body)
                            
                            # Log successful sync (response handling can be added if needed)
                            if hasattr(sync_response, 'success') and not sync_response.success:
                                self._logger.warning(f"Upload sync returned non-success status")
                                
                        except Exception as e:
                            self._logger.warning(f"Failed to sync upload with server: {str(e)}")
                            # Continue anyway as the file was uploaded

                        # Use LoggerStateManager to temporarily activate the logger
                        with LoggerStateManager(self._logger):
                            self._logger.success(
                                f"Uploaded attachment: {attachment_name}"
                            )
                    except Exception as e:
                        # Use LoggerStateManager to temporarily activate the logger
                        with LoggerStateManager(self._logger):
                            self._logger.error(
                                f"Failed to process attachment: {str(e)}"
                            )
                        continue
            return original_upload_id
        except Exception as e:
            self._logger.error(
                f"Otherwise uncaught exception: {str(e)}"
            )
            return ""
