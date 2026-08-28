"""Test custom metadata on part revisions."""

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError, ErrorBADREQUEST
from ..utils import assert_create_revision_success
from ...parts.utils import assert_create_part_success
from ...utils import assert_station_access_forbidden
from ....e2e_tag import uid


def _make_part(client: TofuPilot, timestamp: str) -> str:
    """Create a part and return its number."""
    number = f"RMETA-{timestamp}-{uid()}"
    result = client.parts.create(number=number, name="Revision Metadata Part")
    assert_create_part_success(result)
    return number


def _make_revision(client: TofuPilot, part_number: str) -> str:
    """Create a revision on `part_number` and return its number."""
    number = f"REV-{uid()}"
    result = client.parts.revisions.create(part_number=part_number, number=number)
    assert_create_revision_success(result)
    return number


class TestRevisionMetadata:

    def test_create_revision_with_metadata(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Metadata dict survives round-trip with native types."""
        part_number = _make_part(client, timestamp)
        revision_number = f"REV-{uid()}"
        result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number,
            metadata={"ecn": "ECN-2041", "yield": 98.5, "released": True},
        )
        assert_create_revision_success(result)

        revision = client.parts.revisions.get(
            part_number=part_number, revision_number=revision_number
        )
        assert revision.metadata is not None
        assert revision.metadata["ecn"] == "ECN-2041"
        assert revision.metadata["yield"] == 98.5
        assert revision.metadata["released"] is True

    def test_get_revision_without_metadata_returns_empty(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """A revision created without metadata reports none, not an error."""
        part_number = _make_part(client, timestamp)
        revision_number = _make_revision(client, part_number)
        revision = client.parts.revisions.get(
            part_number=part_number, revision_number=revision_number
        )
        assert not revision.metadata

    def test_update_metadata_patch_preserves_other_keys(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """PATCH semantics: keys not present in payload stay on the entity."""
        if auth_type == "station":
            with assert_station_access_forbidden("update revision metadata"):
                client.parts.revisions.update(
                    part_number="any", revision_number="any", metadata={"a": "first"}
                )
            return

        part_number = _make_part(client, timestamp)
        revision_number = _make_revision(client, part_number)
        client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            metadata={"a": "first", "b": "second"},
        )
        client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            metadata={"a": "updated"},
        )
        revision = client.parts.revisions.get(
            part_number=part_number, revision_number=revision_number
        )
        assert revision.metadata == {"a": "updated", "b": "second"}

    def test_update_metadata_null_deletes_key(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Passing null as a value deletes that key."""
        if auth_type == "station":
            return

        part_number = _make_part(client, timestamp)
        revision_number = _make_revision(client, part_number)
        client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            metadata={"keep": "me", "drop": "later"},
        )
        client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            metadata={"drop": None},
        )
        revision = client.parts.revisions.get(
            part_number=part_number, revision_number=revision_number
        )
        assert revision.metadata == {"keep": "me"}

    def test_update_metadata_does_not_touch_number(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """A metadata-only PATCH leaves the revision number untouched."""
        if auth_type == "station":
            return

        part_number = _make_part(client, timestamp)
        revision_number = _make_revision(client, part_number)
        client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            metadata={"ecn": "ECN-2041"},
        )
        revision = client.parts.revisions.get(
            part_number=part_number, revision_number=revision_number
        )
        assert revision.number == revision_number
        assert revision.metadata == {"ecn": "ECN-2041"}

    def test_update_metadata_type_change_on_existing_key(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Server allows changing the type of an existing key."""
        if auth_type == "station":
            return

        part_number = _make_part(client, timestamp)
        revision_number = _make_revision(client, part_number)
        client.parts.revisions.update(
            part_number=part_number, revision_number=revision_number, metadata={"flag": "yes"}
        )
        client.parts.revisions.update(
            part_number=part_number, revision_number=revision_number, metadata={"flag": True}
        )
        revision = client.parts.revisions.get(
            part_number=part_number, revision_number=revision_number
        )
        assert revision.metadata is not None
        assert revision.metadata["flag"] is True

    def test_metadata_invalid_key_chars_rejected(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Keys outside [a-zA-Z0-9_.:+-] are rejected at the API boundary."""
        if auth_type == "station":
            return

        part_number = _make_part(client, timestamp)
        revision_number = _make_revision(client, part_number)
        with pytest.raises((ErrorBADREQUEST, APIError)):
            client.parts.revisions.update(
                part_number=part_number,
                revision_number=revision_number,
                metadata={"has space": "nope"},
            )

    def test_metadata_max_50_keys(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """50-key cap is enforced before any DB write."""
        if auth_type == "station":
            return

        part_number = _make_part(client, timestamp)
        revision_number = _make_revision(client, part_number)
        too_many = {f"k{i}": i for i in range(51)}
        with pytest.raises((ErrorBADREQUEST, APIError)):
            client.parts.revisions.update(
                part_number=part_number, revision_number=revision_number, metadata=too_many
            )
        # Confirm nothing was written
        revision = client.parts.revisions.get(
            part_number=part_number, revision_number=revision_number
        )
        assert not revision.metadata
