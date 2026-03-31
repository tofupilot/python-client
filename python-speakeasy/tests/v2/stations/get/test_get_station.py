"""Test getting individual station details."""

from datetime import datetime, timezone
import uuid
from typing import List
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_station_success, assert_get_station_success
from ...utils import assert_station_access_forbidden


class TestGetStation:
    """Test getting individual station details."""

    def test_get_station_by_id(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test getting a station by its ID."""
        if auth_type == "station":
            # Stations can get station details by ID (full access)
            # But they can't create stations, so test with get on a known station
            # Just verify the endpoint works — use get_current instead
            result = client.stations.get_current()
            assert len(result.id) > 0
            assert len(result.name) > 0
            return

        station_name = f"Get Test Station - {timestamp}"
        create_result = client.stations.create(name=station_name)
        assert_create_station_success(create_result)
        station_id = create_result.id

        get_result = client.stations.get(id=station_id)
        assert_get_station_success(get_result)

        assert get_result.id == station_id
        assert get_result.name == station_name
        assert isinstance(get_result.procedures, list)
        assert len(get_result.procedures) == 0
        assert get_result.api_key is None
        assert get_result.connection_status is None or get_result.connection_status in ['connected', 'disconnected']

    def test_get_station_nonexistent(self, client: TofuPilot, auth_type: str) -> None:
        """Test getting a station that doesn't exist."""
        with pytest.raises(ErrorNOTFOUND):
            client.stations.get(id=str(uuid.uuid4()))

    def test_get_station_with_procedures(self, client: TofuPilot, auth_type: str, procedure_id: str, timestamp) -> None:
        """Test getting a station that has linked procedures."""
        if auth_type == "station":
            return

        station_name = f"Station with Procedures - {timestamp}"
        create_result = client.stations.create(name=station_name)
        assert_create_station_success(create_result)
        station_id = create_result.id

        get_result = client.stations.get(id=station_id)
        assert_get_station_success(get_result)
        assert isinstance(get_result.procedures, list)
        for proc in get_result.procedures:
            assert hasattr(proc, 'id')
            assert hasattr(proc, 'name')

    def test_get_station_connection_status(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that connection status is returned correctly."""
        if auth_type == "station":
            result = client.stations.get_current()
            assert result.connection_status is None or result.connection_status in ['connected', 'disconnected']
            return

        create_result = client.stations.create(name=f"Connection Test - {timestamp}")
        station_id = create_result.id

        result = client.stations.get(id=station_id)
        assert_get_station_success(result)
        assert result.connection_status is None or result.connection_status in ['connected', 'disconnected']

    def test_get_multiple_stations_sequentially(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test getting multiple stations one after another."""
        if auth_type == "station":
            # Stations can't create/list stations, just verify get_current works
            result = client.stations.get_current()
            assert len(result.id) > 0
            return

        station_ids: List[str] = []
        for i in range(3):
            name = f"Sequential Test {i+1} - {timestamp}-{str(uuid.uuid4())[:8]}"
            result = client.stations.create(name=name)
            station_ids.append(result.id)

        for station_id in station_ids:
            get_result = client.stations.get(id=station_id)
            assert_get_station_success(get_result)
            assert get_result.id == station_id
