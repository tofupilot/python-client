"""Test updating runs."""

import uuid

import pytest
import requests
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ...utils import (
    assert_create_run_success,
    assert_update_run_success,
    get_random_test_dates,
)


def upload_to_presigned_url(upload_url: str, content: bytes, content_type: str = "text/plain") -> None:
    """Upload content to a presigned URL."""
    response = requests.put(
        upload_url,
        data=content,
        headers={"Content-Type": content_type},
    )
    assert response.status_code == 200, f"Upload failed with status {response.status_code}"


class TestUpdateRun:
    """Test updating runs."""

    def test_update_run_with_attachment(self, client: TofuPilot, procedure_id: str) -> None:
        """Test updating a run with an attachment."""
        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]

        create_result = client.runs.create(
            serial_number=f"SN-UPD-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-UPD-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        # Initialize and upload attachment
        attachment = client.attachments.initialize(name="test_report.txt")
        upload_to_presigned_url(
            attachment.upload_url,
            b"Test report content for run attachment.",
        )

        # Update run with attachment
        update_result = client.runs.update(
            id=create_result.id,
            attachments=[attachment.id],
        )
        assert_update_run_success(update_result)
        assert update_result.id == create_result.id

        # Verify attachment is present via get
        get_result = client.runs.get(id=create_result.id)
        assert get_result.attachments is not None
        assert len(get_result.attachments) >= 1

    def test_update_nonexistent_run(self, client: TofuPilot) -> None:
        """Test updating a run that doesn't exist."""
        nonexistent_id = str(uuid.uuid4())

        with pytest.raises(ErrorNOTFOUND):
            client.runs.update(id=nonexistent_id, attachments=[])
