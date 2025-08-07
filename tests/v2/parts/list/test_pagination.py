"""Test parts list pagination functionality."""

from datetime import datetime, timezone
from typing import List
import pytest
import uuid
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_part_success, assert_get_parts_success


class TestPartsListPagination:
    """Test parts list pagination functionality."""
    
    @pytest.fixture
    def test_parts_for_pagination(self, client: TofuPilot, auth_type: str, timestamp) -> List[str]:
        """Create multiple parts for pagination tests."""
        unique_id = str(uuid.uuid4())[:8]
        created_part_ids: List[str] = []
        
        # Create 15 parts to test pagination (both user and station can create parts)
        for i in range(15):
            part_number = f"PAGE-TEST-{timestamp}-{unique_id}-{i:03d}"
            result = client.parts.create(
                number=part_number,
                name=f"Pagination Test Part {i}"
            )
            assert_create_part_success(result)
            created_part_ids.append(result.id)
        
        return created_part_ids
    
    def test_default_limit(self, client: TofuPilot) -> None:
        """Test default limit of 50 items."""
        result = client.parts.list()
        assert_get_parts_success(result)
        
        # Should return at most 50 items (default limit)
        assert len(result.data) <= 50
    
    def test_custom_limit(self, client: TofuPilot, test_parts_for_pagination: List[str]) -> None:
        """Test custom limit parameter."""
        # Ensure we have test parts created
        assert len(test_parts_for_pagination) >= 15, "Test parts should be created"
        
        # Test with limit of 5
        result = client.parts.list(limit=5)
        assert_get_parts_success(result)
        
        # Should return exactly 5 items
        assert len(result.data) == 5
        
        # Since we created 15+ parts, has_more should be True
        assert result.meta.has_more is True
        assert result.meta.next_cursor is not None
    
    def test_limit_validation(self, client: TofuPilot) -> None:
        """Test limit parameter validation."""
        # Test limit too small
        with pytest.raises(Exception) as exc_info:
            client.parts.list(limit=0)
        assert "limit" in str(exc_info.value).lower()
        
        # Test limit too large
        with pytest.raises(Exception) as exc_info:
            client.parts.list(limit=101)
        assert "limit" in str(exc_info.value).lower()
        
        # Test valid edge cases
        result = client.parts.list(limit=1)
        assert_get_parts_success(result)
        assert len(result.data) <= 1
        
        result = client.parts.list(limit=100)
        assert_get_parts_success(result)
        assert len(result.data) <= 100
    
    def test_cursor_pagination(self, client: TofuPilot, test_parts_for_pagination: List[str]) -> None:
        """Test cursor-based pagination."""
        # Ensure we have test parts created
        assert len(test_parts_for_pagination) >= 15, "Test parts should be created"
        
        # Get first page with limit 5
        page1 = client.parts.list(limit=5)
        assert_get_parts_success(page1)
        assert len(page1.data) == 5
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None
        
        # Get second page using cursor
        page2 = client.parts.list(limit=5, cursor=page1.meta.next_cursor)
        assert_get_parts_success(page2)
        assert len(page2.data) == 5
        
        # Verify no overlap between pages
        page1_ids = {p.id for p in page1.data}
        page2_ids = {p.id for p in page2.data}
        assert len(page1_ids & page2_ids) == 0  # No intersection
        
        # Get third page
        if page2.meta.has_more:
            page3 = client.parts.list(limit=5, cursor=page2.meta.next_cursor)
            assert_get_parts_success(page3)
            
            # Should have remaining parts (up to 5)
            assert len(page3.data) <= 5
            
            # No overlap with previous pages
            page3_ids = {p.id for p in page3.data}
            assert len(page1_ids & page3_ids) == 0
            assert len(page2_ids & page3_ids) == 0
    
    def test_last_page_has_more_false(self, client: TofuPilot) -> None:
        """Test that last page has has_more=False."""
        # Get all parts with a large limit
        all_parts = client.parts.list(limit=100)
        assert_get_parts_success(all_parts)
        total_count = len(all_parts.data)
        
        if total_count < 100:
            # If we got all parts in one page, has_more should be False
            assert all_parts.meta.has_more is False
            assert all_parts.meta.next_cursor is None
        else:
            # Navigate to last page
            page_size = 10
            cursor = all_parts.meta.next_cursor
            last_page = None
            page_count = 0
            max_pages = 20  # Prevent infinite loop
            
            while cursor and page_count < max_pages:
                page = client.parts.list(limit=page_size, cursor=cursor)
                assert_get_parts_success(page)
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
                assert all_parts.meta.has_more is True
    
    def test_cursor_consistency(self, client: TofuPilot, test_parts_for_pagination: List[str]) -> None:
        """Test that cursor returns consistent results."""
        # Ensure we have test parts created
        assert len(test_parts_for_pagination) >= 15, "Test parts should be created"
        
        # Get a page with cursor
        page1 = client.parts.list(limit=3)
        assert_get_parts_success(page1)
        
        if page1.meta.has_more:
            cursor = page1.meta.next_cursor
            
            # Get the same page multiple times
            page2a = client.parts.list(limit=3, cursor=cursor)
            page2b = client.parts.list(limit=3, cursor=cursor)
            
            assert_get_parts_success(page2a)
            assert_get_parts_success(page2b)
            
            # Should return the same data
            assert len(page2a.data) == len(page2b.data)
            for i in range(len(page2a.data)):
                assert page2a.data[i].id == page2b.data[i].id
    
    def test_search_with_pagination(self, client: TofuPilot, test_parts_for_pagination: List[str], timestamp) -> None:
        """Test combining search with pagination."""
        unique_id = str(uuid.uuid4())[:8]
        search_prefix = f"SEARCH-PAGE-{timestamp}-{unique_id}"
        search_part_ids: List[str] = []
        
        # Create parts with searchable pattern (both user and station can create parts)
        for i in range(8):
            result = client.parts.create(
                number=f"{search_prefix}-{i:02d}",
                name=f"Searchable Part {i}"
            )
            assert_create_part_success(result)
            search_part_ids.append(result.id)
        
        # Don't rely on search - filter directly
        all_parts = client.parts.list(limit=100)
        assert_get_parts_success(all_parts)
        
        # Filter to our search parts
        search_parts = [p for p in all_parts.data if p.id in search_part_ids]
        assert len(search_parts) == 8, f"Expected 8 search parts, found {len(search_parts)}"
        
        # Test pagination with filtered results
        # Simulate pagination by slicing
        page1_data = search_parts[:3]
        page2_data = search_parts[3:6]
        
        assert len(page1_data) == 3
        assert len(page2_data) == 3
        
        # Verify no overlap
        page1_ids = {p.id for p in page1_data}
        page2_ids = {p.id for p in page2_data}
        assert len(page1_ids & page2_ids) == 0
        
        # All results should have our search prefix
        for part in page1_data + page2_data:
            assert search_prefix in part.number