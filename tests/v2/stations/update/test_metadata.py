"""Test custom metadata on stations."""

import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError, ErrorBADREQUEST, ErrorFORBIDDEN
from ..utils import assert_create_station_success, assert_get_station_success
from ...utils import assert_station_access_forbidden
from ....e2e_tag import uid


def _make_station(client: TofuPilot, timestamp: str) -> str:
    """Create a station and return its id."""
    result = client.stations.create(name=f"Metadata Test Station {timestamp}-{uid()}")
    assert_create_station_success(result)
    return result.id


class TestStationMetadata:

    def test_create_station_with_metadata(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Metadata dict survives round-trip with native types."""
        if auth_type == "station":
            with pytest.raises(ErrorFORBIDDEN):
                client.stations.create(
                    name="Forbidden Station", metadata={"location": "nowhere"}
                )
            return

        result = client.stations.create(
            name=f"Metadata Create Station {timestamp}-{uid()}",
            metadata={
                "location": "Lausanne HQ",
                "rack": 3,
                "calibrated": True,
            },
        )
        assert_create_station_success(result)

        station = client.stations.get(id=result.id)
        assert_get_station_success(station)
        assert station.metadata is not None
        assert station.metadata["location"] == "Lausanne HQ"
        assert station.metadata["rack"] == 3
        assert station.metadata["calibrated"] is True

    def test_get_station_without_metadata_returns_empty(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """A station created without metadata reports none, not an error."""
        if auth_type == "station":
            # Stations can read themselves but cannot create one to compare
            # against; check the field is exposed on the self-read instead.
            station = client.stations.get_current()
            assert station.metadata is None or isinstance(station.metadata, dict)
            return

        station_id = _make_station(client, timestamp)
        station = client.stations.get(id=station_id)
        assert not station.metadata

    def test_update_metadata_patch_preserves_other_keys(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """PATCH semantics: keys not present in payload stay on the entity."""
        if auth_type == "station":
            with assert_station_access_forbidden("update station metadata"):
                client.stations.update(id=str(uuid.uuid4()), metadata={"a": "first"})
            return

        station_id = _make_station(client, timestamp)
        client.stations.update(
            id=station_id,
            metadata={"a": "first", "b": "second"},
        )
        client.stations.update(
            id=station_id,
            metadata={"a": "updated"},
        )
        station = client.stations.get(id=station_id)
        assert station.metadata == {"a": "updated", "b": "second"}

    def test_update_metadata_null_deletes_key(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Passing null as a value deletes that key."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete station metadata key"):
                client.stations.update(id=str(uuid.uuid4()), metadata={"drop": None})
            return

        station_id = _make_station(client, timestamp)
        client.stations.update(
            id=station_id,
            metadata={"keep": "me", "drop": "later"},
        )
        client.stations.update(
            id=station_id,
            metadata={"drop": None},
        )
        station = client.stations.get(id=station_id)
        assert station.metadata == {"keep": "me"}

    def test_update_metadata_does_not_touch_other_fields(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """A metadata-only PATCH leaves the station name untouched."""
        if auth_type == "station":
            with assert_station_access_forbidden("update station metadata"):
                client.stations.update(id=str(uuid.uuid4()), metadata={"site": "A"})
            return

        name = f"Metadata Name Station {timestamp}-{uid()}"
        result = client.stations.create(name=name)
        assert_create_station_success(result)

        update = client.stations.update(id=result.id, metadata={"site": "A"})
        assert update.name == name

        station = client.stations.get(id=result.id)
        assert station.name == name
        assert station.metadata == {"site": "A"}

    def test_update_metadata_type_change_on_existing_key(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Server allows changing the type of an existing key."""
        if auth_type == "station":
            with assert_station_access_forbidden("update station metadata"):
                client.stations.update(id=str(uuid.uuid4()), metadata={"flag": True})
            return

        station_id = _make_station(client, timestamp)
        client.stations.update(id=station_id, metadata={"flag": "yes"})
        client.stations.update(id=station_id, metadata={"flag": True})
        station = client.stations.get(id=station_id)
        assert station.metadata is not None
        assert station.metadata["flag"] is True

    def test_metadata_invalid_key_chars_rejected(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """Keys outside [a-zA-Z0-9_.:+-] are rejected at the API boundary."""
        if auth_type == "station":
            with assert_station_access_forbidden("update station metadata"):
                client.stations.update(id=str(uuid.uuid4()), metadata={"has space": "nope"})
            return

        station_id = _make_station(client, timestamp)
        with pytest.raises((ErrorBADREQUEST, APIError)):
            client.stations.update(
                id=station_id,
                metadata={"has space": "nope"},
            )

    def test_metadata_max_50_keys(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """50-key cap is enforced before any DB write."""
        if auth_type == "station":
            with assert_station_access_forbidden("update station metadata"):
                client.stations.update(id=str(uuid.uuid4()), metadata={"k": 1})
            return

        station_id = _make_station(client, timestamp)
        too_many = {f"k{i}": i for i in range(51)}
        with pytest.raises((ErrorBADREQUEST, APIError)):
            client.stations.update(id=station_id, metadata=too_many)
        # Confirm nothing was written
        station = client.stations.get(id=station_id)
        assert not station.metadata

    def test_list_include_metadata(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """list(include_metadata=True) returns metadata; omitting it leaves the field out."""
        if auth_type == "station":
            with assert_station_access_forbidden("list stations"):
                client.stations.list(include_metadata=True)
            return

        marker = f"site-{uuid.uuid4().hex[:6]}"
        name = f"Metadata List Station {timestamp}-{uid()}"
        result = client.stations.create(name=name, metadata={"site": marker})
        assert_create_station_success(result)

        with_meta = client.stations.list(search_query=name, include_metadata=True)
        matches = [s for s in with_meta.data if s.id == result.id]
        assert len(matches) == 1
        assert matches[0].metadata == {"site": marker}

        without_meta = client.stations.list(search_query=name)
        matches = [s for s in without_meta.data if s.id == result.id]
        assert len(matches) == 1
        assert matches[0].metadata is None

    def test_list_filter_by_metadata(
        self, client: TofuPilot, auth_type: str, timestamp
    ) -> None:
        """list(metadata=...) keeps only stations matching every key; composes with search."""
        if auth_type == "station":
            with assert_station_access_forbidden("list stations"):
                client.stations.list(metadata={"site": {"in": ["x"]}})
            return

        marker = f"site-{uuid.uuid4().hex[:6]}"
        prefix = f"Meta Filter {timestamp}-{uid()}"
        hq = client.stations.create(
            name=f"{prefix} HQ",
            metadata={"site": marker, "rack": 3, "calibrated": True},
        )
        supplier = client.stations.create(
            name=f"{prefix} Supplier",
            metadata={"site": marker, "rack": 12, "calibrated": False},
        )
        bare = client.stations.create(name=f"{prefix} Bare")
        for created in (hq, supplier, bare):
            assert_create_station_success(created)

        def ids(result) -> set:
            return {s.id for s in result.data}

        # string `in` — both tagged stations, not the bare one
        by_site = client.stations.list(
            search_query=prefix, metadata={"site": {"in": [marker]}}
        )
        assert ids(by_site) == {hq.id, supplier.id}

        # several keys AND together (string + number range)
        by_rack = client.stations.list(
            search_query=prefix,
            metadata={"site": {"in": [marker]}, "rack": {"gte": 10}},
        )
        assert ids(by_rack) == {supplier.id}

        # bool, with the metadata echoed back on the filtered rows
        by_bool = client.stations.list(
            search_query=prefix,
            metadata={"site": {"in": [marker]}, "calibrated": {"eq": True}},
            include_metadata=True,
        )
        assert ids(by_bool) == {hq.id}
        assert by_bool.data[0].metadata == {"site": marker, "rack": 3, "calibrated": True}

        # no filter → all three
        assert ids(client.stations.list(search_query=prefix)) == {hq.id, supplier.id, bare.id}
