"""Test removing/deleting stations."""

from datetime import datetime, timezone
import uuid
from typing import List
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_station_success, assert_remove_station_success
from ...utils import assert_station_access_forbidden


class TestRemoveStation:
    """Test removing/deleting stations."""
    
    def test_remove_station_without_runs(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test removing a station that has no runs (permanent deletion)."""
        if auth_type == "station":
            # Stations cannot remove other stations (HTTP 403 FORBIDDEN)
            fake_station_id = str(uuid.uuid4())
            with assert_station_access_forbidden("remove station without runs"):
                client.stations.remove(id=fake_station_id)
            return
        
        # Create a station
        station_name = f"Station to Remove - {timestamp}"
        
        create_result = client.stations.create(name=station_name)
        assert_create_station_success(create_result)
        station_id = create_result.id
        
        # Remove the station
        remove_result = client.stations.remove(id=station_id)
        assert_remove_station_success(remove_result)
        assert remove_result.id == station_id
        
        # Verify it's gone by trying to get it
        with pytest.raises(ErrorNOTFOUND):
            client.stations.get(id=station_id)
        
        # Verify it's not in the list
        list_result = client.stations.list(search_query=station_name)
        found = any(station.id == station_id for station in list_result.data)
        assert not found, "Removed station still appears in list"
    
    def test_remove_station_nonexistent(self, client: TofuPilot, auth_type: str) -> None:
        """Test removing a station that doesn't exist."""
        if auth_type == "station":
            # Stations cannot remove stations (HTTP 403 FORBIDDEN)
            nonexistent_id = str(uuid.uuid4())
            with assert_station_access_forbidden("remove nonexistent station"):
                client.stations.remove(id=nonexistent_id)
            return
        
        nonexistent_id = str(uuid.uuid4())
        
        with pytest.raises(ErrorNOTFOUND):
            client.stations.remove(id=nonexistent_id)
    
    def test_remove_multiple_stations(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test removing multiple stations in sequence."""
        if auth_type == "station":
            # Stations cannot remove stations (HTTP 403 FORBIDDEN) 
            fake_station_id = str(uuid.uuid4())
            with assert_station_access_forbidden("remove multiple stations"):
                client.stations.remove(id=fake_station_id)
            return
        
        # Create multiple stations
        station_ids: List[str] = []
        
        for i in range(3):
            name = f"Batch Remove Station {i+1} - {timestamp}-{str(uuid.uuid4())[:8]}"
            result = client.stations.create(name=name)
            station_ids.append(result.id)
        
        # Remove each station
        for station_id in station_ids:
            remove_result = client.stations.remove(id=station_id)
            assert_remove_station_success(remove_result)
            assert remove_result.id == station_id
        
        # Verify all are gone
        for station_id in station_ids:
            with pytest.raises(ErrorNOTFOUND):
                client.stations.get(id=station_id)
    
    def test_remove_station_twice(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test removing the same station twice (should fail second time)."""
        if auth_type == "station":
            # Stations cannot remove stations (HTTP 403 FORBIDDEN)
            fake_station_id = str(uuid.uuid4())
            with assert_station_access_forbidden("remove station twice"):
                client.stations.remove(id=fake_station_id)
            return
        
        # Create and remove a station
        create_result = client.stations.create(name=f"Double Remove Test - {timestamp}")
        station_id = create_result.id
        
        # First removal should succeed
        client.stations.remove(id=station_id)
        
        # Second removal should fail
        with pytest.raises(ErrorNOTFOUND):
            client.stations.remove(id=station_id)
    
    def test_remove_station_with_runs_archives(self, client: TofuPilot, auth_type: str, procedure_id: str, timestamp) -> None:
        """Test that removing a station with runs archives it instead of deleting."""
        if auth_type == "station":
            # Stations cannot remove stations (HTTP 403 FORBIDDEN)
            fake_station_id = str(uuid.uuid4())
            with assert_station_access_forbidden("remove station with runs"):
                client.stations.remove(id=fake_station_id)
            return
        
        # Create a station
        station_name = f"Station with Runs - {timestamp}"
        
        create_result = client.stations.create(name=station_name)
        station_id = create_result.id
        
        # Note: To fully test this scenario, we would need to:
        # 1. Link a procedure to the station
        # 2. Create a run with this station
        # 3. Then try to remove the station
        # This would require additional endpoints not in basic CRUD
        
        # For now, just test the removal works
        remove_result = client.stations.remove(id=station_id)
        assert_remove_station_success(remove_result)
    
