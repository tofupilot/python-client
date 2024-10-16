import os
import json
import datetime
from typing import Optional

from openhtf.core import test_record
from openhtf.output.callbacks import json_factory
import requests

from .client import TofuPilotClient
from .constants import (
    SECONDS_BEFORE_TIMEOUT,
)
from .utils import (
    notify_server,
)


class UploadToTofuPilot:
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

    def __call__(self, test_record: test_record.TestRecord):

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
        filename = "./{dut_id}.{test_name}.{start_time}.json".format(
            dut_id=dut_id, test_name=test_name, start_time=start_time_formatted
        )

        # Use the existing OutputToJSON callback to write to the custom file
        output_callback = json_factory.OutputToJSON(
            filename,
            inline_attachments=False,  # Exclude raw attachments
            allow_nan=False,  # Customize this flag as needed
        )

        # Open the custom file and write serialized test record to it
        with open(filename, "w") as file:
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
