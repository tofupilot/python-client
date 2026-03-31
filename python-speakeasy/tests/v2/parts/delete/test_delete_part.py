"""Test deleting parts."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_part_success, assert_delete_part_success
from ...utils import assert_station_access_forbidden


class TestDeletePart:
    """Test deleting parts."""

    def test_delete_part(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test deleting a part and verifying it's gone with cascade on revisions."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete part"):
                client.parts.delete(number="any")
            return

        unique_id = str(uuid.uuid4())[:8]
        part_number = f"DEL-PART-{unique_id}-{timestamp}"
        create_result = client.parts.create(
            number=part_number,
            name=f"Delete Test {unique_id}",
            revision_number="A",
        )
        assert_create_part_success(create_result)

        delete_result = client.parts.delete(number=part_number)
        assert_delete_part_success(delete_result)
        assert delete_result.id == create_result.id
        assert len(delete_result.deleted_revision_ids) > 0

        with pytest.raises(ErrorNOTFOUND):
            client.parts.get(number=part_number)

    def test_delete_nonexistent_part(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting a part that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete nonexistent part"):
                client.parts.delete(number="nonexistent")
            return

        fake_number = f"NONEXISTENT-{uuid.uuid4().hex[:8]}"
        with pytest.raises(ErrorNOTFOUND):
            client.parts.delete(number=fake_number)
