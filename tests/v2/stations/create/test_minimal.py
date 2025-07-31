"""Test minimal station creation."""

from datetime import datetime, timezone
import uuid
from typing import List, Dict
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_station_success, assert_get_stations_success


class TestCreateStationMinimal:
    """Test minimal station creation scenarios."""
    
    def test_create_station_minimal(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a station with only required fields (name)."""
        if auth_type == "station":
            # Skip test for station auth
            return
            
        # Test constants - ensure uniqueness with timestamp + uuid
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        STATION_NAME = f"Test Station {timestamp}-{unique_id}"
        
        # Create station using SDK
        result = client.stations.create(
            name=STATION_NAME,
        )
        
        # Verify successful response
        assert_create_station_success(result)
        
        # Test stations.list to verify it's in the list
        list_result = client.stations.list(search_query=STATION_NAME)
        assert_get_stations_success(list_result)
        assert len(list_result.data) >= 1
        
        # Find our created station
        found_station = None
        for station in list_result.data:
            if station.id == result.id:
                found_station = station
                break
        
        assert found_station is not None
        assert found_station.name == STATION_NAME
        # Identifier should be auto-generated with format STA-XXX
        assert found_station.identifier is not None
        assert found_station.identifier.startswith("STA-")
        assert len(found_station.identifier) == 7  # STA-XXX
        # No procedures should be linked yet
        assert found_station.procedures_count == 0
        assert len(found_station.procedures) == 0
        # Image should be None
        assert found_station.image is None
    
    def test_create_multiple_stations(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating multiple stations in sequence."""
        if auth_type == "station":
            # Skip test for station auth
            return
            
        stations_created: List[Dict[str, str]] = []
        
        # Create 3 stations
        for i in range(3):
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
            station_name = f"Station {i+1} - {timestamp}"
            
            result = client.stations.create(name=station_name)
            assert_create_station_success(result)
            stations_created.append({
                'id': result.id,
                'name': station_name
            })
        
        # List all stations and verify they exist
        list_result = client.stations.list(limit=50)
        assert_get_stations_success(list_result)
        
        # Verify all created stations are in the list
        station_ids_in_list = {station.id for station in list_result.data}
        for created_station in stations_created:
            assert created_station['id'] in station_ids_in_list, \
                f"Station {created_station['id']} not found in list"
    
    def test_create_station_with_special_characters(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a station with special characters in name."""
        if auth_type == "station":
            # Skip test for station auth
            return
            
        # Test constants with special characters
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        STATION_NAME = f"Station #1 @Factory & Testing (100%) - {timestamp}"
        
        # Create station
        result = client.stations.create(name=STATION_NAME)
        
        # Verify successful response
        assert_create_station_success(result)
        
        # Search for the station
        list_result = client.stations.list(search_query=STATION_NAME)
        assert_get_stations_success(list_result)
        
        # Find and verify our station
        found = False
        for station in list_result.data:
            if station.id == result.id:
                found = True
                assert station.name == STATION_NAME
                break
        
        assert found, f"Created station {result.id} not found in list"