"""TofuPilot integration with OpenHTF.

`upload()` is an OpenHTF output callback: register it with
`test.add_output_callbacks(upload())` and the run is sent to TofuPilot when
the test finishes.

The `TofuPilot` context manager was removed in 2.15.0. It wrapped this same
callback and added MQTT streaming to the legacy operator UI; the TofuPilot
CLI (`tofupilot run`) provides the live operator UI now, and uploading needs
only the callback.
"""

from ..error_tracking import ApiV1Error
from .upload import upload

# ApiV1Error is re-exported because `upload` raises it when a run fails to
# reach the server. Catching that needed an import from a private-looking
# module before.
__all__ = ["upload", "ApiV1Error"]
