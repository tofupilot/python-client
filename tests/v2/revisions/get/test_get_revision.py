"""Test getting revisions."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_revision_success, assert_get_revision_success
from ...parts.utils import assert_create_part_success


class TestGetRevision:
    """Test getting revisions by part number and revision number."""

    def test_get_revision_by_part_and_number(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test getting a revision and verifying all fields."""
        if auth_type == "station":
            with pytest.raises(ErrorNOTFOUND):
                client.parts.revisions.get(
                    part_number="NONEXISTENT-PART",
                    revision_number="A",
                )
            return

        unique_id = str(uuid.uuid4())[:8]
        part_number = f"GET-REV-{unique_id}-{timestamp}"
        revision_number = f"REV-{unique_id}"

        part = client.parts.create(number=part_number, name=f"Get Revision Test {unique_id}")
        assert_create_part_success(part)

        revision = client.parts.revisions.create(part_number=part_number, number=revision_number)
        assert_create_revision_success(revision)

        result = client.parts.revisions.get(part_number=part_number, revision_number=revision_number)
        assert_get_revision_success(result)

        assert result.id == revision.id
        assert result.number == revision_number
        assert result.created_at is not None
        assert result.part.number == part_number
        assert result.part.id == part.id
        assert isinstance(result.units, list)

    def test_get_nonexistent_revision(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test getting a revision that doesn't exist."""
        if auth_type == "station":
            with pytest.raises(ErrorNOTFOUND):
                client.parts.revisions.get(
                    part_number="NONEXISTENT-PART",
                    revision_number="nonexistent",
                )
            return

        unique_id = str(uuid.uuid4())[:8]
        part_number = f"GET-REV-NF-{unique_id}-{timestamp}"

        part = client.parts.create(number=part_number, name=f"Nonexistent Rev Test {unique_id}")
        assert_create_part_success(part)

        with pytest.raises(ErrorNOTFOUND):
            client.parts.revisions.get(
                part_number=part_number,
                revision_number="nonexistent-rev",
            )
