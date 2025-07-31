"""Basic integration tests for station CRUD operations."""

from datetime import datetime, timezone
import uuid
from tofupilot.v2 import TofuPilot
from .utils import (
    assert_create_station_success,
    assert_get_stations_success,
    assert_get_station_success,
    assert_update_station_success,
    assert_remove_station_success
)


class TestStationBasicOperations:
    """Test basic CRUD operations for stations."""
    
    def test_station_full_lifecycle(self, client: TofuPilot, auth_type: str) -> None:
        """Test complete station lifecycle: create, read, update, delete."""
        if auth_type == "station":
            # Skip test for station auth as they can't create/update/delete
            return
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        # 1. Create a station
        station_name = f"Lifecycle Test Station - {timestamp}-{unique_id}"
        create_result = client.stations.create(name=station_name)
        assert_create_station_success(create_result)
        station_id = create_result.id
        
        # 2. List stations and verify it exists
        list_result = client.stations.list(search_query=station_name)
        assert_get_stations_success(list_result)
        assert any(s.id == station_id for s in list_result.data)
        
        # 3. Get the station by ID
        get_result = client.stations.get(id=station_id)
        assert_get_station_success(get_result)
        assert get_result.name == station_name
        # Save original identifier for comparison
        # original_identifier = get_result.identifier
        
        # 4. Update the station
        new_name = f"Updated {station_name}"
        new_identifier = f"STA-{unique_id[:3].upper()}"
        update_result = client.stations.update(
            id=station_id,
            name=new_name,
            identifier=new_identifier
        )
        assert_update_station_success(update_result)
        assert update_result.name == new_name
        assert update_result.identifier == new_identifier
        
        # 5. Verify update via get
        get_updated = client.stations.get(id=station_id)
        assert get_updated.name == new_name
        assert get_updated.identifier == new_identifier
        
        # 6. Remove the station
        remove_result = client.stations.remove(id=station_id)
        assert_remove_station_success(remove_result)
        
        # 7. Verify it's gone from list
        final_list = client.stations.list(search_query=new_name)
        assert not any(s.id == station_id for s in final_list.data)
    
    def test_station_list_and_search_operations(self, client: TofuPilot, auth_type: str) -> None:
        """Test various list and search operations."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            from ..utils import assert_station_access_forbidden
            with assert_station_access_forbidden("list stations"):
                client.stations.list()
            return
        
        # 1. List all stations with default parameters
        default_list = client.stations.list()
        assert_get_stations_success(default_list)
        # Record initial count for reference
        # initial_count = len(default_list.data)
        
        # 2. List with custom limit
        limited_list = client.stations.list(limit=5)
        assert_get_stations_success(limited_list)
        assert len(limited_list.data) <= 5
        
        # 3. Search for stations containing "Station"
        search_result = client.stations.list(search_query="Station")
        assert_get_stations_success(search_result)
        # All results should contain "station" (case-insensitive)
        for station in search_result.data:
            combined = f"{station.name} {station.identifier}".lower()
            assert "station" in combined
        
        # 4. Test pagination if there are enough stations
        if default_list.meta.has_more:
            page2 = client.stations.list(cursor=default_list.meta.next_cursor)
            assert_get_stations_success(page2)
            # Ensure different stations on page 2
            page1_ids = {s.id for s in default_list.data}
            page2_ids = {s.id for s in page2.data}
            assert len(page1_ids.intersection(page2_ids)) == 0
    
    def test_station_data_integrity(self, client: TofuPilot, auth_type: str) -> None:
        """Test that station data maintains integrity across operations."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            from ..utils import assert_station_access_forbidden
            with assert_station_access_forbidden("list stations"):
                client.stations.list(limit=1)
            return
        
        # For user auth, create and verify data integrity
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        station_name = f"Data Integrity Test - {timestamp}"
        
        # Create station
        create_result = client.stations.create(name=station_name)
        station_id = create_result.id
        
        # Get full details
        full_details = client.stations.get(id=station_id)
        
        # Verify all expected fields are present and correct types
        assert isinstance(full_details.id, str)
        assert isinstance(full_details.name, str)
        assert isinstance(full_details.identifier, str)
        assert isinstance(full_details.procedures, list)
        assert full_details.api_key is None or isinstance(full_details.api_key, str)
        assert full_details.image is None or isinstance(full_details.image, dict)
        assert full_details.connection_status is None or full_details.connection_status in ['connected', 'disconnected']
        
        # Clean up
        client.stations.remove(id=station_id)