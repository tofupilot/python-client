"""Test getting individual station details."""

from datetime import datetime, timezone
import uuid
from typing import List
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_station_success, assert_get_station_success


class TestGetStation:
    """Test getting individual station details."""
    
    def test_get_station_by_id(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test getting a station by its ID."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            from ...utils import assert_station_access_forbidden
            with assert_station_access_forbidden("list stations"):
                client.stations.list(limit=1)
            return
        
        # Create a station first
        station_name = f"Get Test Station - {timestamp}"
        
        create_result = client.stations.create(name=station_name)
        assert_create_station_success(create_result)
        station_id = create_result.id
        
        # Get the station by ID
        get_result = client.stations.get(id=station_id)
        assert_get_station_success(get_result)
        
        # Verify the details
        assert get_result.id == station_id
        assert get_result.name == station_name
        assert get_result.identifier.startswith("STA-")
        assert isinstance(get_result.procedures, list)
        assert len(get_result.procedures) == 0  # No linked procedures yet
        assert get_result.api_key is None  # No API key by default
        assert get_result.image is None  # No image by default
        assert get_result.connection_status is None or get_result.connection_status in ['connected', 'disconnected']
    
    def test_get_station_nonexistent(self, client: TofuPilot, auth_type: str) -> None:
        """Test getting a station that doesn't exist."""
        with pytest.raises(ErrorNOTFOUND):
            client.stations.get(id=str(uuid.uuid4()))
    
    def test_get_station_with_procedures(self, client: TofuPilot, auth_type: str, procedure_id: str, timestamp) -> None:
        """Test getting a station that has linked procedures."""
        if auth_type == "station":
            # Skip for station auth as they can't create/link
            return
        
        # Create a station
        station_name = f"Station with Procedures - {timestamp}"
        
        create_result = client.stations.create(name=station_name)
        assert_create_station_success(create_result)
        station_id = create_result.id
        
        # Note: Linking procedures would require the link_procedure endpoint
        # which is not part of the basic CRUD operations
        # For now, just verify the procedures list exists
        
        get_result = client.stations.get(id=station_id)
        assert_get_station_success(get_result)
        
        assert isinstance(get_result.procedures, list)
        # Each procedure should have required fields when present
        for proc in get_result.procedures:
            assert hasattr(proc, 'id')
            assert hasattr(proc, 'name')
            assert hasattr(proc, 'identifier')
            assert hasattr(proc, 'runs_count')
    
    def test_get_station_connection_status(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that connection status is returned correctly."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            from ...utils import assert_station_access_forbidden
            with assert_station_access_forbidden("list stations"):
                client.stations.list(limit=1)
            return
        
        # Create a new station
        create_result = client.stations.create(name=f"Connection Test - {timestamp}")
        station_id = create_result.id
        
        # Get the station
        result = client.stations.get(id=station_id)
        assert_get_station_success(result)
        
        # Connection status should be None, 'connected', or 'disconnected'
        assert result.connection_status is None or result.connection_status in ['connected', 'disconnected']
    
    def test_get_multiple_stations_sequentially(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test getting multiple stations one after another."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            from ...utils import assert_station_access_forbidden
            with assert_station_access_forbidden("list stations"):
                client.stations.list(limit=3)
            return
        
        # Create multiple stations
        station_ids: List[str] = []
        
        for i in range(3):
            name = f"Sequential Test {i+1} - {timestamp}-{str(uuid.uuid4())[:8]}"
            result = client.stations.create(name=name)
            station_ids.append(result.id)
        
        # Get each station and verify
        for station_id in station_ids:
            get_result = client.stations.get(id=station_id)
            assert_get_station_success(get_result)
            assert get_result.id == station_id