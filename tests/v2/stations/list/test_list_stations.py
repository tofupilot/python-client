"""Test listing and filtering stations."""

import uuid
import pytest
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_station_success, assert_get_stations_success
from ...utils import assert_station_access_forbidden


class TestListStations:
    """Test listing and filtering stations."""

    def test_list_all_stations(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test listing stations returns a paginated response."""
        if auth_type == "station":
            with assert_station_access_forbidden("list stations"):
                client.stations.list(limit=10)
            return

        # Ensure at least one station exists
        client.stations.create(name=f"List All Test - {timestamp}")

        result = client.stations.list(limit=10)
        assert_get_stations_success(result)
        assert len(result.data) > 0
        assert hasattr(result.meta, "has_more")
        assert hasattr(result.meta, "next_cursor")

        # Verify data fields
        station = result.data[0]
        assert len(station.id) > 0
        assert len(station.identifier) > 0
        assert len(station.name) > 0
        assert isinstance(station.procedures, list)

    def test_list_with_search_query(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test filtering stations by search query on name/identifier."""
        if auth_type == "station":
            with assert_station_access_forbidden("list stations"):
                client.stations.list(search_query="test")
            return

        unique_name = f"SearchableStation-{timestamp}-{uuid.uuid4().hex[:8]}"
        create_result = client.stations.create(name=unique_name)
        assert_create_station_success(create_result)

        result = client.stations.list(search_query=unique_name)
        assert_get_stations_success(result)

        found_ids = [s.id for s in result.data]
        assert create_result.id in found_ids

    def test_list_pagination(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test cursor-based pagination for stations list."""
        if auth_type == "station":
            with assert_station_access_forbidden("list stations"):
                client.stations.list(limit=1)
            return

        # Create 3 stations with unique names for filtering
        unique_prefix = f"PagStation-{timestamp}-{uuid.uuid4().hex[:6]}"
        created_ids = []
        for i in range(3):
            result = client.stations.create(name=f"{unique_prefix}-{i}")
            created_ids.append(result.id)

        # First page
        page1 = client.stations.list(search_query=unique_prefix, limit=1)
        assert_get_stations_success(page1)
        assert len(page1.data) == 1
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None

        # Second page
        page2 = client.stations.list(
            search_query=unique_prefix,
            limit=1,
            cursor=page1.meta.next_cursor,
        )
        assert_get_stations_success(page2)
        assert len(page2.data) == 1
        assert page2.data[0].id != page1.data[0].id
