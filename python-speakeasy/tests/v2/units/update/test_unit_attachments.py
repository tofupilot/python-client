"""Test attaching files to units via the v2 API.

This test demonstrates the full attachment workflow:
1. Initialize an upload to get a pre-signed URL
2. Upload file content to storage
3. Finalize the upload
4. Link the attachment to a unit
5. Verify the attachment appears on the unit
"""

import requests as http_requests
from tofupilot.v2 import TofuPilot
from ..utils import assert_update_unit_success, assert_get_unit_success
from ...utils import assert_station_access_forbidden


class TestUnitAttachments:
    """Test the full unit attachment workflow."""

    def test_attach_file_to_unit(self, client: TofuPilot, auth_type: str, create_test_unit, timestamp) -> None:
        """Attach a file to a unit and verify it appears on the unit."""
        if auth_type == "station":
            with assert_station_access_forbidden("update unit with attachment"):
                client.units.update(serial_number="any", attachments=["fake-id"])
            return

        _, serial, _ = create_test_unit("ATTACH")

        # Step 1: Initialize upload
        init = client.attachments.initialize(name="test_report.txt")
        assert init.id
        assert init.upload_url

        # Step 2: Upload file content to the pre-signed URL
        file_content = b"Hello from TofuPilot unit attachment test!"
        put_resp = http_requests.put(
            init.upload_url,
            data=file_content,
            headers={"Content-Type": "text/plain"},
        )
        assert put_resp.status_code == 200, f"Upload failed: {put_resp.status_code}"

        # Step 3: Finalize the upload
        result = client.attachments.finalize(id=init.id)
        assert result.url

        # Step 4: Link attachment to the unit
        update = client.units.update(
            serial_number=serial,
            attachments=[init.id],
        )
        assert_update_unit_success(update)

        # Step 5: Verify attachment appears on the unit
        unit = client.units.get(serial_number=serial)
        assert_get_unit_success(unit)
        assert unit.attachments is not None
        assert len(unit.attachments) >= 1
        attached = next((a for a in unit.attachments if a.id == init.id), None)
        assert attached is not None
        assert attached.name == "test_report.txt"
