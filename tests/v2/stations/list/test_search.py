"""Test station list search functionality."""

from datetime import datetime, timezone
import uuid
from typing import List
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_station_success, assert_get_stations_success


class TestStationListSearch:
    """Test station list search scenarios."""
    
    def test_search_station_by_name(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test searching stations by name."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            from ...utils import assert_station_access_forbidden
            with assert_station_access_forbidden("list stations"):
                client.stations.list(search_query="Assembly")
            return
        
        # Create test stations with specific names
        unique_id = str(uuid.uuid4())[:8]
        
        test_stations = [
            f"Assembly Station Alpha - {timestamp}-{unique_id}",
            f"Testing Station Beta - {timestamp}-{unique_id}",
            f"Assembly Station Gamma - {timestamp}-{unique_id}",
            f"Quality Control Delta - {timestamp}-{unique_id}"
        ]
        
        created_ids: List[str] = []
        for name in test_stations:
            result = client.stations.create(name=name)
            assert_create_station_success(result)
            created_ids.append(result.id)
        
        # Search for "Assembly" - should find 2 stations
        search_result = client.stations.list(search_query="Assembly")
        assert_get_stations_success(search_result)
        
        # Count matching stations from our test set
        matching_count = 0
        for station in search_result.data:
            if station.id in created_ids and "assembly" in station.name.lower():
                matching_count += 1
        
        assert matching_count == 2, f"Expected 2 Assembly stations, found {matching_count}"
    
    def test_search_station_by_identifier(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test searching stations by identifier."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            from ...utils import assert_station_access_forbidden
            with assert_station_access_forbidden("list stations"):
                client.stations.list(search_query="STA-")
            return
        
        # Create a station and get its auto-generated identifier
        station_name = f"Search Test Station - {timestamp}"
        
        create_result = client.stations.create(name=station_name)
        assert_create_station_success(create_result)
        
        # List to get the identifier
        list_result = client.stations.list(search_query=station_name)
        assert_get_stations_success(list_result)
        
        created_station = None
        for station in list_result.data:
            if station.id == create_result.id:
                created_station = station
                break
        
        assert created_station is not None
        identifier = created_station.identifier
        
        # Search by identifier
        search_result = client.stations.list(search_query=identifier)
        assert_get_stations_success(search_result)
        
        # Verify the station is found
        found = False
        for station in search_result.data:
            if station.id == create_result.id:
                found = True
                assert station.identifier == identifier
                break
        
        assert found, f"Station with identifier {identifier} not found in search results"
    
    def test_search_station_partial_match(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test partial matching in station search."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            from ...utils import assert_station_access_forbidden
            with assert_station_access_forbidden("list stations"):
                client.stations.list(search_query="Stat")
            return
        
        # Create stations with related names
        base_name = f"Manufacture-{timestamp}"
        
        test_names = [
            f"{base_name}-Manufacturing",
            f"{base_name}-Manufacturer",
            f"{base_name}-Manufactured"
        ]
        
        for name in test_names:
            result = client.stations.create(name=name)
            assert_create_station_success(result)
        
        # Search with partial term
        search_result = client.stations.list(search_query=base_name)
        assert_get_stations_success(search_result)
        
        # Count matches
        match_count = 0
        for station in search_result.data:
            if base_name in station.name:
                match_count += 1
        
        assert match_count >= 3, f"Expected at least 3 matches for '{base_name}', found {match_count}"
    
    def test_search_station_no_results(self, client: TofuPilot, auth_type: str) -> None:
        """Test search that returns no results."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            from ...utils import assert_station_access_forbidden
            with assert_station_access_forbidden("list stations"):
                unique_search = f"NonexistentStation{uuid.uuid4()}"
                client.stations.list(search_query=unique_search)
            return
        
        # Search for a term that shouldn't exist
        unique_search = f"NonexistentStation{uuid.uuid4()}"
        
        result = client.stations.list(search_query=unique_search)
        assert_get_stations_success(result)
        
        # Should return empty results
        assert len(result.data) == 0
        assert result.meta.has_more is False
        assert result.meta.next_cursor is None