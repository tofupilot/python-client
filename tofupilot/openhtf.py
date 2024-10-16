"""
This module handles all TofuPilot methods related to integration with OpenHTF.

It provides two main classes:
1. tofupilot.upload(): A way to interface with OpenHTF test scripts to automatically upload test results to the TofuPilot server.
2. tofupilot.TofuPilot(): A way to stream real-time execution data of OpenHTF tests to TofuPilot for live monitoring.
"""

import os
import json
import datetime
from typing import Optional
import threading
import time

import openhtf
from openhtf.core.test_record import TestRecord
from openhtf.output.callbacks import json_factory
import requests

from .client import TofuPilotClient
from .constants import (
    SECONDS_BEFORE_TIMEOUT,
)
from .utils import (
    notify_server,
)


class upload:  # pylint: disable=invalid-name
    """
    OpenHTF output callback to automatically upload the test report to TofuPilot upon test completion.

    This function behaves similarly to manually parsing the OpenHTF JSON test report and calling
    `TofuPilotClient().create_run()` with the parsed data, streamlining the process for automatic uploads.

    ### Usage Example:

    ```python
    from openhtf import test
    import tofupilot

    # ...

    def main():
        test = Test(*your_phases, procedure_id="FVT1")

        # Add TofuPilot's upload callback to automatically send the test report upon completion
        test.add_output_callback(tofupilot.upload())

        test.execute(lambda: "SN15")
    ```
    """

    def __init__(self, allow_nan=False, base_url: Optional[str] = None):
        self.allow_nan = allow_nan
        self.client = (
            TofuPilotClient(base_url=base_url) if base_url else TofuPilotClient()
        )
        self._logger = self.client._logger
        self._base_url = self.client._base_url
        self._headers = self.client._headers
        self._max_attachments = self.client._max_attachments
        self._max_file_size = self.client._max_file_size

    def __call__(self, test_record: TestRecord):

        # Extract relevant details from the test record
        dut_id = test_record.dut_id
        test_name = test_record.metadata.get("test_name")

        # Convert milliseconds to a datetime object
        start_time = datetime.datetime.fromtimestamp(
            test_record.start_time_millis / 1000.0
        )

        # Format the timestamp as YYYY-MM-DD_HH_MM_SS_SSS
        start_time_formatted = start_time.strftime("%Y-%m-%d_%H-%M-%S-%f")[
            :-3
        ]  # Use underscores for time, slice for milliseconds precision

        # Format the custom file name
        filename = f"./{dut_id}.{test_name}.{start_time_formatted}.json"

        # Use the existing OutputToJSON callback to write to the custom file
        output_callback = json_factory.OutputToJSON(
            filename,
            inline_attachments=False,  # Exclude raw attachments
            allow_nan=False,  # Customize this flag as needed
        )

        # Open the custom file and write serialized test record to it
        with open(filename, "w", encoding="utf-8") as file:
            for json_line in output_callback.serialize_test_record(test_record):
                file.write(json_line)

        try:
            # Call create_run_from_report with the generated file path
            run_id = self.client.create_run_from_openhtf_report(filename)
        finally:
            # Ensure the file is deleted after processing
            if os.path.exists(filename):
                os.remove(filename)

        if run_id:
            number_of_attachments = 0
            for phase in test_record.phases:
                # Keep only max number of attachments
                if number_of_attachments >= self._max_attachments:
                    self._logger.warning(
                        "Too many attachments, trimming to %d attachments.",
                        self._max_attachments,
                    )
                    break
                for attachment_name, attachment in phase.attachments.items():
                    # Remove attachments that exceed the max file size
                    if attachment.size > self._max_file_size:
                        self._logger.warning(
                            "File size exceeds the maximum allowed size of %d bytes: %s",
                            self._max_file_size,
                            attachment.name,
                        )
                        continue
                    if number_of_attachments >= self._max_attachments:
                        break

                    number_of_attachments += 1

                    self._logger.info("Uploading %s...", attachment_name)

                    # Upload initialization
                    initialize_url = f"{self._base_url}/uploads/initialize"
                    payload = {"name": attachment_name}

                    response = requests.post(
                        initialize_url,
                        data=json.dumps(payload),
                        headers=self._headers,
                        timeout=SECONDS_BEFORE_TIMEOUT,
                    )

                    response.raise_for_status()
                    response_json = response.json()
                    upload_url = response_json.get("uploadUrl")
                    upload_id = response_json.get("id")

                    requests.put(
                        upload_url,
                        data=attachment.data,
                        headers={"Content-Type": attachment.mimetype},
                        timeout=SECONDS_BEFORE_TIMEOUT,
                    )

                    notify_server(self._headers, self._base_url, upload_id, run_id)

                    self._logger.success(
                        "Attachment %s successfully uploaded and linked to run.",
                        attachment_name,
                    )


def _get_executing_test():
    """Get the currently executing test and its state.
    See: https://github.com/google/openhtf/blob/4706af6c186340abf1735c992b2f1a3a11068e52/openhtf/output/servers/station_server.py

    When this function returns, it is not guaranteed that the returned test is
    still running. A consumer of this function that wants to access test.state is
    exposed to a race condition in which test.state may become None at any time
    due to the test finishing. To address this, in addition to returning the test
    itself, this function returns the last known test state.

    Returns:
      test: The test that was executing when this function was called, or None.
      test_state: The state of the executing test, or None.
    """
    tests = list(openhtf.Test.TEST_INSTANCES.values())

    if not tests:
        return None, None

    test = tests[0]
    test_state = test.state

    if test_state is None:
        # This is the case if:
        # 1. The test executor was created but has not started running.
        # 2. The test finished while this function was running, after we got the
        #        list of tests but before we accessed the test state.
        return None, None

    return test, test_state


class TofuPilot:
    """
    Context manager to automatically add an output callback to the running OpenHTF test.


    ### Usage Example:

    ```python
    from openhtf import Test
    from tofupilot import TofuPilot

    #...

    def main():
        test = Test(*your_phases, procedure_id="FVT1")

        # Stream real-time test execution data to TofuPilot
        with TofuPilot():
            test.execute(lambda: "SN15")
    ```
    """

    def __init__(self, base_url=None):
        self.base_url = base_url
        self.test = None
        self.timeout = 10
        self.watcher_thread = None
        self.stop_event = threading.Event()

    def __enter__(self):
        test, _ = _get_executing_test()
        self.test = test
        # Start a watcher thread to monitor the test state
        self.watcher_thread = threading.Thread(target=self._watch_for_test_start)
        self.watcher_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Stop the watcher thread when exiting
        self.stop_event.set()
        self.watcher_thread.join()

    def _watch_for_test_start(self):
        """Watch for the test to start and add the output callback when it does."""
        start_time = time.time()

        while not self.stop_event.is_set():
            test, _ = _get_executing_test()
            self.test = test

            if self.test is not None:
                # Add the output callback when the test starts
                self.test.add_output_callbacks(upload(base_url=self.base_url))
                return

            # Check for timeout
            if time.time() - start_time > self.timeout:
                raise RuntimeError(
                    "Timeout: No OpenHTF test started within the timeout period."
                )

            # Sleep briefly to avoid busy-waiting
            time.sleep(0.1)
