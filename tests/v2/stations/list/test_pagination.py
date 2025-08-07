"""Test station list pagination."""

from datetime import datetime, timezone
import uuid
import pytest
from typing import List, Optional, Any
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_station_success, assert_get_stations_success
from ...utils import assert_station_access_forbidden


class TestStationListPagination:
    """Test station list pagination scenarios."""
    
    @pytest.fixture
    def test_stations_for_pagination(self, client: TofuPilot, auth_type: str, timestamp) -> List[str]:
        """Create multiple stations for pagination tests."""
        if auth_type == "station":
            # Station can't create stations, return empty list
            return []

        unique_id = str(uuid.uuid4())[:8]
        created_station_ids: List[str] = []
        
        # Create 15 stations to test pagination
        for i in range(15):
            station_name = f"PAGE-TEST-{timestamp}-{unique_id}-{i:03d}"
            result = client.stations.create(name=station_name)
            assert_create_station_success(result)
            created_station_ids.append(result.id)
        
        return created_station_ids
    
    def test_default_limit(self, client: TofuPilot, auth_type: str) -> None:
        """Test default limit of 50 items."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            with assert_station_access_forbidden("list stations"):
                client.stations.list()
            return
            
        result = client.stations.list()
        assert_get_stations_success(result)
        
        # Should return at most 50 items (default limit)
        assert len(result.data) <= 50
    
    def test_custom_limit(self, client: TofuPilot, test_stations_for_pagination: List[str], auth_type: str) -> None:
        """Test custom limit parameter."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            with assert_station_access_forbidden("list stations with custom limit"):
                client.stations.list(limit=5)
            return
        
        # Ensure we have test stations created
        assert len(test_stations_for_pagination) >= 15, "Test stations should be created"
        
        # Test with limit of 5
        result = client.stations.list(limit=5)
        assert_get_stations_success(result)
        
        # Should return exactly 5 items
        assert len(result.data) == 5
        
        # Since we created 15+ stations, has_more should be True
        assert result.meta.has_more is True
        assert result.meta.next_cursor is not None
    
    def test_cursor_pagination(self, client: TofuPilot, test_stations_for_pagination: List[str], auth_type: str) -> None:
        """Test cursor-based pagination."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            with assert_station_access_forbidden("list stations with pagination"):
                client.stations.list(limit=2)
            return
            
        # Ensure we have test stations created
        assert len(test_stations_for_pagination) >= 15, "Test stations should be created"
        
        # Get first page with limit 5
        page1 = client.stations.list(limit=5)
        assert_get_stations_success(page1)
        assert len(page1.data) == 5
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None
        
        # Get second page using cursor
        page2 = client.stations.list(limit=5, cursor=page1.meta.next_cursor)
        assert_get_stations_success(page2)
        assert len(page2.data) == 5
        
        # Verify no overlap between pages
        page1_ids = {s.id for s in page1.data}
        page2_ids = {s.id for s in page2.data}
        assert len(page1_ids & page2_ids) == 0  # No intersection
        
        # Get third page
        if page2.meta.has_more:
            page3 = client.stations.list(limit=5, cursor=page2.meta.next_cursor)
            assert_get_stations_success(page3)
            
            # Should have remaining stations (up to 5)
            assert len(page3.data) <= 5
            
            # No overlap with previous pages
            page3_ids = {s.id for s in page3.data}
            assert len(page1_ids & page3_ids) == 0
            assert len(page2_ids & page3_ids) == 0
    
    def test_limit_validation(self, client: TofuPilot, auth_type: str) -> None:
        """Test limit parameter validation."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            with assert_station_access_forbidden("list stations with limit=0"):
                client.stations.list(limit=0)
            return
            
        # Test limit too small
        with pytest.raises(Exception) as exc_info:
            client.stations.list(limit=0)
        assert "limit" in str(exc_info.value).lower()
        
        # Test limit too large
        with pytest.raises(Exception) as exc_info:
            client.stations.list(limit=101)
        assert "limit" in str(exc_info.value).lower()
        
        # Test valid edge cases
        result = client.stations.list(limit=1)
        assert_get_stations_success(result)
        assert len(result.data) <= 1
        
        result = client.stations.list(limit=100)
        assert_get_stations_success(result)
        assert len(result.data) <= 100
    
    def test_last_page_has_more_false(self, client: TofuPilot, auth_type: str) -> None:
        """Test that last page has has_more=False."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            with assert_station_access_forbidden("list stations with large limit"):
                client.stations.list(limit=100)
            return
            
        # Get all stations with a large limit
        all_stations = client.stations.list(limit=100)
        assert_get_stations_success(all_stations)
        total_count = len(all_stations.data)
        
        if total_count < 100:
            # If we got all stations in one page, has_more should be False
            assert all_stations.meta.has_more is False
            assert all_stations.meta.next_cursor is None
        else:
            # Navigate to last page
            page_size = 10
            cursor = all_stations.meta.next_cursor
            last_page = None
            page_count = 0
            max_pages = 20  # Prevent infinite loop
            
            while cursor and page_count < max_pages:
                page = client.stations.list(limit=page_size, cursor=cursor)
                assert_get_stations_success(page)
                page_count += 1
                
                if not page.meta.has_more:
                    last_page = page
                    break
                
                cursor = page.meta.next_cursor
            
            # If we found a last page, verify it
            if last_page:
                assert last_page.meta.has_more is False
                assert last_page.meta.next_cursor is None
            # Otherwise just verify we have pagination working
            else:
                assert all_stations.meta.has_more is True
    
    def test_cursor_consistency(self, client: TofuPilot, test_stations_for_pagination: List[str], auth_type: str) -> None:
        """Test that cursor returns consistent results."""
        if auth_type == "station":
            # Stations cannot list other stations - should get 403 Forbidden
            with assert_station_access_forbidden("list stations for consistency test"):
                client.stations.list(limit=3)
            return
        
        # Ensure we have test stations created
        assert len(test_stations_for_pagination) >= 15, "Test stations should be created"
        
        # Get a page with cursor
        page1 = client.stations.list(limit=3)
        assert_get_stations_success(page1)
        
        if page1.meta.has_more:
            cursor = page1.meta.next_cursor
            
            # Get the same page multiple times
            page2a = client.stations.list(limit=3, cursor=cursor)
            page2b = client.stations.list(limit=3, cursor=cursor)
            
            assert_get_stations_success(page2a)
            assert_get_stations_success(page2b)
            
            # Should return the same data
            assert len(page2a.data) == len(page2b.data)
            for i in range(len(page2a.data)):
                assert page2a.data[i].id == page2b.data[i].id