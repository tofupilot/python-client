import os
import json
import datetime
import tempfile
from typing import Optional

from openhtf.core.test_record import TestRecord
from openhtf.output.callbacks import json_factory
import requests

from ..client import TofuPilotClient
from ..constants import (
    SECONDS_BEFORE_TIMEOUT,
)
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
        self.client = client or TofuPilotClient(api_key=api_key, url=url)
        self._logger = self.client._logger
        self._url = self.client._url
        self._headers = self.client._headers
        self._verify = verify  # Kept for backward compatibility
        self._max_attachments = self.client._max_attachments
        self._max_file_size = self.client._max_file_size

    def __call__(self, test_record: TestRecord):
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
                # Call create_run_from_report with the generated file path
                result = self.client.upload_and_create_from_openhtf_report(filename)

                # Extract run_id from response - it could be a string (id) or a dict (result with id field)
                run_id = None

                if isinstance(result, dict):
                    # It's a dictionary response
                    if not result.get("success", True):
                        self._logger.error("Run creation failed, skipping attachments")
                        return

                    # Try to get the ID from the dictionary
                    run_id = result.get("id")
                else:
                    # Direct ID string
                    run_id = result

                # Final validation of run_id
                if not run_id or not isinstance(run_id, str):
                    self._logger.error(
                        f"Invalid run ID received: {run_id}, skipping attachments"
                    )
                    return
            except Exception as e:
                self._logger.error(f"Error creating run: {str(e)}")
                return
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

                    # Upload initialization
                    initialize_url = f"{self._url}/uploads/initialize"
                    payload = {"name": attachment_name}

                    try:
                        response = requests.post(
                            initialize_url,
                            data=json.dumps(payload),
                            headers=self._headers,
                            verify=self._verify,
                            timeout=SECONDS_BEFORE_TIMEOUT,
                        )

                        response.raise_for_status()
                        response_json = response.json()
                        upload_url = response_json.get("uploadUrl")
                        upload_id = response_json.get("id")

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

                        notify_server(
                            self._headers,
                            self._url,
                            upload_id,
                            run_id,
                            logger=self._logger,
                        )

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
        finally:
            # For attachment logs to be visible, we intentionally don't pause the logger here
            # Instead, we'll let the TofuPilot class's __exit__ method handle the logger state
            pass
