"""Test deleting revisions."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_revision_success, assert_delete_revision_success
from ...parts.utils import assert_create_part_success
from ...utils import assert_station_access_forbidden


class TestDeleteRevision:
    """Test deleting revisions."""

    def test_delete_revision(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test deleting a revision and verifying it's gone."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete revision"):
                client.parts.revisions.delete(
                    part_number="any",
                    revision_number="any",
                )
            return

        unique_id = str(uuid.uuid4())[:8]
        part_number = f"DEL-REV-{unique_id}-{timestamp}"
        revision_number = f"REV-{unique_id}"

        part = client.parts.create(number=part_number, name=f"Delete Revision Test {unique_id}")
        assert_create_part_success(part)

        revision = client.parts.revisions.create(part_number=part_number, number=revision_number)
        assert_create_revision_success(revision)

        delete_result = client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
        assert_delete_revision_success(delete_result)
        assert delete_result.id == revision.id

        with pytest.raises(ErrorNOTFOUND):
            client.parts.revisions.get(part_number=part_number, revision_number=revision_number)

    def test_delete_nonexistent_revision(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test deleting a revision that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete nonexistent revision"):
                client.parts.revisions.delete(
                    part_number="any",
                    revision_number="nonexistent",
                )
            return

        unique_id = str(uuid.uuid4())[:8]
        part_number = f"DEL-REV-NF-{unique_id}-{timestamp}"

        part = client.parts.create(number=part_number, name=f"Delete Rev NotFound Test {unique_id}")
        assert_create_part_success(part)

        with pytest.raises(ErrorNOTFOUND):
            client.parts.revisions.delete(
                part_number=part_number,
                revision_number="nonexistent-rev",
            )
