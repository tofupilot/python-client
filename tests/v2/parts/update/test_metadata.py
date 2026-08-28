"""Test custom metadata on parts."""

import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError, ErrorBADREQUEST
from ..utils import assert_create_part_success
from ...utils import assert_station_access_forbidden
from ....e2e_tag import uid


def _make_part(client: TofuPilot, timestamp: str) -> str:
    """Create a part and return its number."""
    number = f"PMETA-{timestamp}-{uid()}"
    result = client.parts.create(number=number, name="Metadata Test Part")
    assert_create_part_success(result)
    return number


class TestPartMetadata:

    def test_create_part_with_metadata(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Metadata dict survives round-trip with native types."""
        number = f"PMETA-CREATE-{timestamp}-{uid()}"
        result = client.parts.create(
            number=number,
            name="Metadata Create Part",
            metadata={"supplier": "Acme", "moq": 500, "rohs": True},
        )
        assert_create_part_success(result)

        part = client.parts.get(number=number)
        assert part.metadata is not None
        assert part.metadata["supplier"] == "Acme"
        assert part.metadata["moq"] == 500
        assert part.metadata["rohs"] is True

    def test_get_part_without_metadata_returns_empty(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """A part created without metadata reports none, not an error."""
        number = _make_part(client, timestamp)
        part = client.parts.get(number=number)
        assert not part.metadata

    def test_update_metadata_patch_preserves_other_keys(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """PATCH semantics: keys not present in payload stay on the entity."""
        if auth_type == "station":
            with assert_station_access_forbidden("update part metadata"):
                client.parts.update(number="any", metadata={"a": "first"})
            return

        number = _make_part(client, timestamp)
        client.parts.update(number=number, metadata={"a": "first", "b": "second"})
        client.parts.update(number=number, metadata={"a": "updated"})
        part = client.parts.get(number=number)
        assert part.metadata == {"a": "updated", "b": "second"}

    def test_update_metadata_null_deletes_key(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Passing null as a value deletes that key."""
        if auth_type == "station":
            return

        number = _make_part(client, timestamp)
        client.parts.update(number=number, metadata={"keep": "me", "drop": "later"})
        client.parts.update(number=number, metadata={"drop": None})
        part = client.parts.get(number=number)
        assert part.metadata == {"keep": "me"}

    def test_update_metadata_does_not_touch_other_fields(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """A metadata-only PATCH leaves number and name untouched."""
        if auth_type == "station":
            return

        number = _make_part(client, timestamp)
        update = client.parts.update(number=number, metadata={"site": "A"})
        assert update.number == number
        assert update.name == "Metadata Test Part"

        part = client.parts.get(number=number)
        assert part.name == "Metadata Test Part"
        assert part.metadata == {"site": "A"}

    def test_update_metadata_type_change_on_existing_key(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Server allows changing the type of an existing key."""
        if auth_type == "station":
            return

        number = _make_part(client, timestamp)
        client.parts.update(number=number, metadata={"flag": "yes"})
        client.parts.update(number=number, metadata={"flag": True})
        part = client.parts.get(number=number)
        assert part.metadata is not None
        assert part.metadata["flag"] is True

    def test_metadata_invalid_key_chars_rejected(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Keys outside [a-zA-Z0-9_.:+-] are rejected at the API boundary."""
        if auth_type == "station":
            return

        number = _make_part(client, timestamp)
        with pytest.raises((ErrorBADREQUEST, APIError)):
            client.parts.update(number=number, metadata={"has space": "nope"})

    def test_metadata_max_50_keys(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """50-key cap is enforced before any DB write."""
        if auth_type == "station":
            return

        number = _make_part(client, timestamp)
        too_many = {f"k{i}": i for i in range(51)}
        with pytest.raises((ErrorBADREQUEST, APIError)):
            client.parts.update(number=number, metadata=too_many)
        # Confirm nothing was written
        part = client.parts.get(number=number)
        assert not part.metadata

    def test_list_include_metadata(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """list(include_metadata=True) returns metadata; omitting it leaves the field out."""
        marker = f"site-{uuid.uuid4().hex[:6]}"
        number = f"PMETA-LIST-{timestamp}-{uid()}"
        result = client.parts.create(number=number, metadata={"site": marker})
        assert_create_part_success(result)

        with_meta = client.parts.list(search_query=number, include_metadata=True)
        matches = [p for p in with_meta.data if p.id == result.id]
        assert len(matches) == 1
        assert matches[0].metadata == {"site": marker}

        without_meta = client.parts.list(search_query=number)
        matches = [p for p in without_meta.data if p.id == result.id]
        assert len(matches) == 1
        assert matches[0].metadata is None

    def test_list_filter_by_metadata(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """list(metadata=...) keeps only parts matching every key; composes with search."""
        marker = f"site-{uuid.uuid4().hex[:6]}"
        prefix = f"PMETA-FILTER-{timestamp}-{uid()}"
        acme = client.parts.create(
            number=f"{prefix}-ACME",
            metadata={"site": marker, "moq": 500, "rohs": True},
        )
        beta = client.parts.create(
            number=f"{prefix}-BETA",
            metadata={"site": marker, "moq": 1200, "rohs": False},
        )
        bare = client.parts.create(number=f"{prefix}-BARE")
        for created in (acme, beta, bare):
            assert_create_part_success(created)

        def ids(result) -> set:
            return {p.id for p in result.data}

        # string `in` — both tagged parts, not the bare one
        by_site = client.parts.list(
            search_query=prefix, metadata={"site": {"in": [marker]}}
        )
        assert ids(by_site) == {acme.id, beta.id}

        # several keys AND together (string + number range)
        by_moq = client.parts.list(
            search_query=prefix,
            metadata={"site": {"in": [marker]}, "moq": {"gte": 1000}},
        )
        assert ids(by_moq) == {beta.id}

        # bool, with the metadata echoed back on the filtered rows
        by_bool = client.parts.list(
            search_query=prefix,
            metadata={"site": {"in": [marker]}, "rohs": {"eq": True}},
            include_metadata=True,
        )
        assert ids(by_bool) == {acme.id}
        assert by_bool.data[0].metadata == {"site": marker, "moq": 500, "rohs": True}

        # no filter → all three
        assert ids(client.parts.list(search_query=prefix)) == {acme.id, beta.id, bare.id}
