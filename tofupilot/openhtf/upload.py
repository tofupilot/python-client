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
    LoggerStateManager,
    upload_attachment_data,
    process_openhtf_attachments,
)


class upload:  # pylint: disable=invalid-name
    """
    OpenHTF output callback to automatically upload the test report to TofuPilot upon test completion.

    This function behaves similarly to manually parsing the OpenHTF JSON test report and calling
    `TofuPilotClient().create_run()` with the parsed data.

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
    ):
        self.allow_nan = allow_nan
        self.client = client or TofuPilotClient(api_key=api_key, url=url)
        self._logger = self.client._logger
        self._url = self.client._url
        self._headers = self.client._headers
        self._max_attachments = self.client._max_attachments
        self._max_file_size = self.client._max_file_size

    def __call__(self, test_record: TestRecord):
        # Use context manager to handle logger state
        with LoggerStateManager(self._logger):
            # Extract test metadata
            dut_id = test_record.dut_id
            test_name = test_record.metadata.get("test_name")
            
            # Create timestamp for filename
            start_time = datetime.datetime.fromtimestamp(
                test_record.start_time_millis / 1000.0
            )
            start_time_formatted = start_time.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

            # Create temp file for the report
            fd, filename = tempfile.mkstemp(
                suffix=".json",
                prefix=f"{dut_id}.{test_name}.{start_time_formatted}.",
                dir=tempfile.gettempdir()
            )
            try:
                os.close(fd)  # Close file descriptor
                
                # Use OpenHTF JSON callback to serialize test record
                output_callback = json_factory.OutputToJSON(
                    filename,
                    inline_attachments=False,
                    allow_nan=self.allow_nan,
                    indent=4,
                )
                
                # Write test record to file
                with open(filename, "w", encoding="utf-8") as file:
                    for json_line in output_callback.serialize_test_record(test_record):
                        file.write(json_line)
                
                # Upload report to server
                run_id = self.client.upload_and_create_from_openhtf_report(filename)
                
                # Check if response indicates error
                if isinstance(run_id, dict) and not run_id.get('success', True):
                    return
            except Exception as e:
                self._logger.error(str(e))
                return
            finally:
                # Clean up temp file
                if os.path.exists(filename):
                    os.remove(filename)
                    
        # Skip attachment upload if run_id is invalid
        if not run_id or not isinstance(run_id, str):
            return
            
        # Use the centralized function to process all attachments
        # OpenHTF test record is directly passed as an object, not JSON
        process_openhtf_attachments(
            self._logger,
            self._headers,
            self._url,
            test_record,
            run_id,
            self._max_attachments,
            self._max_file_size,
            needs_base64_decode=False  # Direct object attachments don't need base64 decoding
        )
