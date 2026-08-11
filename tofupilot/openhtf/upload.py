import os
import sys
import datetime
import tempfile
import warnings
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover - types only, never imported at runtime
    from openhtf.core.test_record import TestRecord

from ..v1.client import TofuPilotClient
from ..v1.utils.files import process_openhtf_attachments
from ..error_tracking import ApiV1Error

import posthog


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
            Only used when the callback constructs its own client; when `client`
            is passed, the client's CA bundle applies to the whole upload.

    ### Usage Example:

    ```python
    from openhtf import Test
    from tofupilot.openhtf import upload

    # ...

    def main():
        test = Test(*your_phases, procedure_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")  # procedure UUID from the dashboard

        # Add TofuPilot's upload callback to automatically send the test report upon completion
        test.add_output_callbacks(upload())

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
        # Attachment uploads verify TLS with the client's CA bundle, always.
        # The run POST goes through the client, so verifying attachments
        # against anything else (e.g. a different `verify` argument alongside
        # a passed-in client) would split TLS trust between the two halves of
        # one upload — the run lands but every attachment fails TLS. When we
        # construct the client ourselves, its `_verify` IS the `verify`
        # argument, so this is the same value in every coherent case.
        # warnings.warn, not the client logger: the logger may be paused at
        # construction time, which would swallow the only signal that the
        # verify argument was discarded.
        if client is not None and verify is not None and verify != client._verify:
            warnings.warn(
                "upload(client=..., verify=...): the verify argument is "
                "ignored — the client's CA bundle is used for the whole "
                "upload. Pass verify to TofuPilotClient(...) instead.",
                UserWarning,
                stacklevel=2,
            )
        self._verify = self.client._verify
        self._max_attachments = self.client._max_attachments
        self._max_file_size = self.client._max_file_size

    def __call__(self, test_record: "TestRecord") -> str:
        """
        Returns:
            str:
                Id of the initial upload
                (This id is present in the ApiCall table of the database)
        """
        # The TofuPilot wrapper pauses the client logger for the duration of
        # the test; resume it so upload progress is visible, and restore the
        # paused state afterwards so later runs inside the same with-block
        # stay quiet. The explicit flag (set by pause()/resume()) is the
        # source of truth — inferring paused state from the handler list
        # breaks when host code adds or clears handlers on the singleton.
        was_logger_paused = getattr(self._logger, "_tp_paused", False)
        if hasattr(self._logger, "resume"):
            self._logger.resume()

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

            # Craft system-agnostic temporary filename. dut_id and test_name
            # are user data and land in a path: a lot-prefixed serial like
            # "LOT-1/SN15" — ordinary in manufacturing — produced a path whose
            # parent does not exist, so open() raised FileNotFoundError, the
            # outer handler swallowed it, and the run was silently never
            # uploaded. Anything that is not filename-safe becomes "_".
            def _safe(part, fallback):
                text = str(part) if part is not None else ""
                cleaned = "".join(
                    c if (c.isalnum() or c in "-_.") else "_" for c in text
                ).strip("._")
                return cleaned[:100] or fallback

            filename = os.path.join(
                temp_dir,
                f"{_safe(dut_id, 'unknown-dut')}."
                f"{_safe(test_name, 'unknown-test')}."
                f"{start_time_formatted}.json",
            )

            # OpenHTF's own serializer, imported here rather than at module
            # scope. It is the one part of this file that genuinely needs the
            # framework — it produces the exact record shape the server parses
            # — and importing it lazily keeps `from tofupilot.openhtf import
            # upload` working on an install without openhtf, so the failure
            # names the missing package at the point of use.
            from openhtf.output.callbacks import json_factory

            output_callback = json_factory.OutputToJSON(
                filename,
                inline_attachments=False,  # Exclude raw attachments
                allow_nan=self.allow_nan,
            )

            # Open the custom file and write serialized test record to it
            with open(filename, "w", encoding="utf-8") as file:
                for json_line in output_callback.serialize_test_record(test_record):
                    file.write(json_line)

            try:
                # Call create_run_from_report with the generated file path
                result = self.client._upload_and_create_from_openhtf_report(filename)

                # Extract run_id from response - it could be a string (id) or a dict (result with id field)
                run_id = None

                if not result.get("success", False):
                    # The run never reached the server. Returning the upload id
                    # here reported success with the data silently lost. Raise
                    # so the outer handler logs it and prints the stderr
                    # banner. (Note the limit: OpenHTF catches output-callback
                    # exceptions and finishes with the phases' outcome, so
                    # this cannot flip a PASS — the banner is the operator's
                    # only console signal.)
                    raise ApiV1Error(
                        "Run creation failed; the run was not uploaded"
                    )

                run_id = result.get("run_id")
                original_upload_id: str = result.get("upload_id")

            except Exception as e:
                posthog.capture_exception(e)
                self._logger.error(f"Error creating run: {e}")
                # Propagate to the outer handler, which owns the operator-
                # visible signal. Returning "" here reported the run as
                # uploaded when it was not.
                raise
            finally:
                # Ensure the file is deleted after processing
                if os.path.exists(filename):
                    os.remove(filename)

            # Attachments go through the shared v1 pipeline. This loop used to
            # be a hand-rolled copy of it and had already drifted: it passed
            # the raw `verify` path to requests, skipping the certifi merge in
            # `prepare_verify_setting`, so a custom CA became the entire trust
            # store on this path only and presigned uploads to publicly-signed
            # storage hosts failed TLS.
            process_openhtf_attachments(
                self._logger,
                self._headers,
                self._url,
                test_record,
                run_id,
                self._max_attachments,
                self._max_file_size,
                needs_base64_decode=False,
                verify=self._verify,
            )
            return original_upload_id
        except Exception as e:
            posthog.capture_exception(e)
            self._logger.error(f"Upload failed: {e}")
            # Honesty about what raising achieves: OpenHTF catches output-
            # callback exceptions ("Output callback ... raised; continuing"),
            # so the test still finishes with whatever outcome its phases
            # produced and the process still exits 0 — a raise alone cannot
            # turn a lost upload into a visible failure. It does get the full
            # traceback into the log instead of a bare return, and the banner
            # below is the one signal an operator watching the console gets
            # that this run never reached the server.
            sys.stderr.write(
                "\nERROR: TofuPilot upload failed — this test's run was NOT "
                f"uploaded: {e}\n"
            )
            raise
        finally:
            if was_logger_paused and hasattr(self._logger, "pause"):
                self._logger.pause()
