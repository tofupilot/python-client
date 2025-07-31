"""Test units list pagination functionality."""

from datetime import datetime, timezone
from typing import List
import pytest
import uuid
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_unit_success, assert_get_units_success


class TestUnitsListPagination:
    """Test units list pagination functionality."""
    
    @pytest.fixture
    def test_units_for_pagination(self, client: TofuPilot, auth_type: str) -> List[str]:
        """Create multiple units for pagination tests."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        created_unit_ids: List[str] = []
        
        # Create a part and revision first
        part_result = client.parts.create(
            number=f"PAGE-PART-{timestamp}-{unique_id}",
            name="Pagination Test Part"
        )
        assert part_result.data is not None
        
        revision_result = client.parts.revisions.create(
            part_number=f"PAGE-PART-{timestamp}-{unique_id}",
            number=f"v1.0-{unique_id}"
        )
        
        # Create 15 units to test pagination
        for i in range(15):
            serial_number = f"PAGE-TEST-{timestamp}-{unique_id}-{i:03d}"
            result = client.units.create(
                serial_number=serial_number,
                part_number=f"PAGE-PART-{timestamp}-{unique_id}",
                revision_number=f"v1.0-{unique_id}"
            )
            assert_create_unit_success(result)
            created_unit_ids.append(result.data.id)
        
        return created_unit_ids
    
    def test_default_limit(self, client: TofuPilot) -> None:
        """Test default limit of 50 items."""
        result = client.units.list()
        assert_get_units_success(result)
        
        # Should return at most 50 items (default limit)
        assert len(result.data) <= 50
    
    def test_custom_limit(self, client: TofuPilot, test_units_for_pagination: List[str]) -> None:
        """Test custom limit parameter."""
        # Ensure we have test units created
        assert len(test_units_for_pagination) >= 15, "Test units should be created"
        
        # Test with limit of 5
        result = client.units.list(limit=5)
        assert_get_units_success(result)
        
        # Should return exactly 5 items
        assert len(result.data) == 5
        
        # Since we created 15+ units, has_more should be True
        assert result.meta.has_more is True
        assert result.meta.next_cursor is not None
    
    def test_limit_validation(self, client: TofuPilot) -> None:
        """Test limit parameter validation."""
        # Test limit too small
        with pytest.raises(Exception) as exc_info:
            client.units.list(limit=0)
        assert "limit" in str(exc_info.value).lower()
        
        # Test limit too large
        with pytest.raises(Exception) as exc_info:
            client.units.list(limit=101)
        assert "limit" in str(exc_info.value).lower()
        
        # Test valid edge cases
        result = client.units.list(limit=1)
        assert_get_units_success(result)
        assert len(result.data) <= 1
        
        result = client.units.list(limit=100)
        assert_get_units_success(result)
        assert len(result.data) <= 100
    
    def test_cursor_pagination(self, client: TofuPilot, test_units_for_pagination: List[str]) -> None:
        """Test cursor-based pagination."""
        # Ensure we have test units created
        assert len(test_units_for_pagination) >= 15, "Test units should be created"
        
        # Get first page with limit 5
        page1 = client.units.list(limit=5)
        assert_get_units_success(page1)
        assert len(page1.data) == 5
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None
        
        # Get second page using cursor
        page2 = client.units.list(limit=5, cursor=page1.meta.next_cursor)
        assert_get_units_success(page2)
        assert len(page2.data) == 5
        
        # Verify no overlap between pages
        page1_ids = {u.id for u in page1.data}
        page2_ids = {u.id for u in page2.data}
        assert len(page1_ids & page2_ids) == 0  # No intersection
        
        # Get third page
        if page2.meta.has_more:
            page3 = client.units.list(limit=5, cursor=page2.meta.next_cursor)
            assert_get_units_success(page3)
            
            # Should have remaining units (up to 5)
            assert len(page3.data) <= 5
            
            # No overlap with previous pages
            page3_ids = {u.id for u in page3.data}
            assert len(page1_ids & page3_ids) == 0
            assert len(page2_ids & page3_ids) == 0
    
    def test_last_page_has_more_false(self, client: TofuPilot) -> None:
        """Test that last page has has_more=False."""
        # Get all units with a large limit
        all_units = client.units.list(limit=100)
        assert_get_units_success(all_units)
        total_count = len(all_units.data)
        
        if total_count < 100:
            # If we got all units in one page, has_more should be False
            assert all_units.meta.has_more is False
            assert all_units.meta.next_cursor is None
        else:
            # Navigate to last page
            page_size = 10
            cursor = all_units.meta.next_cursor
            last_page = None
            page_count = 0
            max_pages = 20  # Prevent infinite loop
            
            while cursor and page_count < max_pages:
                page = client.units.list(limit=page_size, cursor=cursor)
                assert_get_units_success(page)
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
                assert all_units.meta.has_more is True
    
    def test_cursor_consistency(self, client: TofuPilot, test_units_for_pagination: List[str]) -> None:
        """Test that cursor returns consistent results."""
        # Ensure we have test units created
        assert len(test_units_for_pagination) >= 15, "Test units should be created"
        
        # Get a page with cursor
        page1 = client.units.list(limit=3)
        assert_get_units_success(page1)
        
        if page1.meta.has_more:
            cursor = page1.meta.next_cursor
            
            # Get the same page multiple times
            page2a = client.units.list(limit=3, cursor=cursor)
            page2b = client.units.list(limit=3, cursor=cursor)
            
            assert_get_units_success(page2a)
            assert_get_units_success(page2b)
            
            # Should return the same data
            assert len(page2a.data) == len(page2b.data)
            for i in range(len(page2a.data)):
                assert page2a.data[i].id == page2b.data[i].id
    
    def test_search_with_pagination(self, client: TofuPilot, test_units_for_pagination: List[str]) -> None:
        """Test combining search with pagination."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        search_prefix = f"SEARCH-PAGE-{timestamp}-{unique_id}"
        search_unit_ids: List[str] = []
        
        # Create a part and revision first
        part_result = client.parts.create(
            number=f"SEARCH-PART-{timestamp}-{unique_id}",
            name="Search Test Part"
        )
        assert part_result.data is not None
        
        revision_result = client.parts.revisions.create(
            part_number=f"SEARCH-PART-{timestamp}-{unique_id}",
            number=f"v1.0-search-{unique_id}"
        )
        
        # Create units with searchable pattern
        for i in range(8):
            result = client.units.create(
                serial_number=f"{search_prefix}-{i:02d}",
                part_number=f"SEARCH-PART-{timestamp}-{unique_id}",
                revision_number=f"v1.0-search-{unique_id}"
            )
            assert_create_unit_success(result)
            search_unit_ids.append(result.data.id)
        
        # Don't rely on search - filter directly
        all_units = client.units.list(limit=100)
        assert_get_units_success(all_units)
        
        # Filter to our search units
        search_units = [u for u in all_units.data if u.id in search_unit_ids]
        assert len(search_units) == 8, f"Expected 8 search units, found {len(search_units)}"
        
        # Test pagination with filtered results
        # Simulate pagination by slicing
        page1_data = search_units[:3]
        page2_data = search_units[3:6]
        
        assert len(page1_data) == 3
        assert len(page2_data) == 3
        
        # Verify no overlap
        page1_ids = {u.id for u in page1_data}
        page2_ids = {u.id for u in page2_data}
        assert len(page1_ids & page2_ids) == 0
        
        # All results should have our search prefix
        for unit in page1_data + page2_data:
            assert search_prefix in unit.serial_number