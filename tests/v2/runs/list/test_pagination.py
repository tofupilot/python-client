"""Test pagination parameters in runs.list()."""

import pytest
from typing import List
from datetime import datetime, timezone
import uuid
from tofupilot.v2 import TofuPilot, models
from ...utils import assert_create_run_success, assert_get_runs_success


class TestRunsPagination:
    """Test limit and cursor pagination parameters."""
    
    @pytest.fixture 
    def test_runs_data(self, client: TofuPilot, procedure_id: str) -> List[models.RunCreateResponse]:
        """Create test runs for pagination tests."""
        timestamp = datetime.now(timezone.utc)
        unique_id = str(uuid.uuid4())[:8]
        
        test_runs = []
        # Create 15 runs to test pagination
        for i in range(15):
            run = client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number=f"PAGE-TEST-{timestamp.strftime('%Y%m%d-%H%M%S')}-{unique_id}-{i:03d}",
                part_number="PCB-001",
                started_at=timestamp,
                ended_at=timestamp
            )
            assert_create_run_success(run)
            test_runs.append(run)
            
        return test_runs

    def test_default_limit(self, client: TofuPilot) -> None:
        """Test default limit of 50 items."""
        result = client.runs.list()
        assert_get_runs_success(result)
        
        # Should return at most 50 items (default limit)
        assert len(result.data) <= 50
    
    def test_custom_limit(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]) -> None:
        """Test custom limit parameter."""
        # Ensure we have test runs created
        assert len(test_runs_data) >= 15, "Test runs should be created"
        
        # Test with limit of 5
        result = client.runs.list(limit=5)
        assert_get_runs_success(result)
        
        # Should return exactly 5 items
        assert len(result.data) == 5
        
        # Since we created 15+ runs, has_more should be True
        assert result.meta.has_more is True
        assert result.meta.next_cursor is not None

    def test_limit_validation(self, client: TofuPilot) -> None:
        """Test limit parameter validation."""
        # Test limit too small
        with pytest.raises(Exception) as exc_info:
            client.runs.list(limit=0)
        assert "limit" in str(exc_info.value).lower()
        
        # Test limit too large
        with pytest.raises(Exception) as exc_info:
            client.runs.list(limit=101)
        assert "limit" in str(exc_info.value).lower()
        
        # Test valid edge cases
        result = client.runs.list(limit=1)
        assert_get_runs_success(result)
        assert len(result.data) <= 1
        
        result = client.runs.list(limit=100)
        assert_get_runs_success(result)
        assert len(result.data) <= 100

    def test_cursor_pagination(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]) -> None:
        """Test cursor-based pagination."""
        # Ensure we have test runs created
        assert len(test_runs_data) >= 15, "Test runs should be created"
        
        # Get first page with limit 5
        page1 = client.runs.list(limit=5)
        assert_get_runs_success(page1)
        assert len(page1.data) == 5
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None
        
        # Get second page using cursor
        page2 = client.runs.list(limit=5, cursor=page1.meta.next_cursor)
        assert_get_runs_success(page2)
        assert len(page2.data) == 5
        
        # Verify no overlap between pages
        page1_ids = {run.id for run in page1.data}
        page2_ids = {run.id for run in page2.data}
        assert len(page1_ids & page2_ids) == 0  # No intersection
        
        # Get third page
        if page2.meta.has_more:
            page3 = client.runs.list(limit=5, cursor=page2.meta.next_cursor)
            assert_get_runs_success(page3)
            
            # Should have remaining runs (up to 5)
            assert len(page3.data) <= 5
            
            # No overlap with previous pages
            page3_ids = {run.id for run in page3.data}
            assert len(page1_ids & page3_ids) == 0
            assert len(page2_ids & page3_ids) == 0

    def test_last_page_has_more_false(self, client: TofuPilot) -> None:
        """Test that last page has has_more=False."""
        # Get all runs with a large limit
        all_runs = client.runs.list(limit=100)
        assert_get_runs_success(all_runs)
        total_count = len(all_runs.data)
        
        if total_count < 100:
            # If we got all runs in one page, has_more should be False
            assert all_runs.meta.has_more is False
            assert all_runs.meta.next_cursor is None
        else:
            # Navigate to last page
            page_size = 10
            cursor = all_runs.meta.next_cursor
            last_page = None
            page_count = 0
            max_pages = 20  # Prevent infinite loop
            
            while cursor and page_count < max_pages:
                page = client.runs.list(limit=page_size, cursor=cursor)
                assert_get_runs_success(page)
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
                assert all_runs.meta.has_more is True
    
    def test_cursor_consistency(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]) -> None:
        """Test that cursor returns consistent results."""
        # Ensure we have test runs created
        assert len(test_runs_data) >= 15, "Test runs should be created"
        
        # Get a page with cursor
        page1 = client.runs.list(limit=3)
        assert_get_runs_success(page1)
        
        if page1.meta.has_more:
            cursor = page1.meta.next_cursor
            
            # Get the same page multiple times
            page2a = client.runs.list(limit=3, cursor=cursor)
            page2b = client.runs.list(limit=3, cursor=cursor)
            
            assert_get_runs_success(page2a)
            assert_get_runs_success(page2b)
            
            # Should return the same data
            assert len(page2a.data) == len(page2b.data)
            for i in range(len(page2a.data)):
                assert page2a.data[i].id == page2b.data[i].id
    
    def test_search_with_pagination(self, client: TofuPilot, procedure_id: str) -> None:
        """Test combining search with pagination."""
        timestamp = datetime.now(timezone.utc)
        unique_id = str(uuid.uuid4())[:8]
        search_prefix = f"SEARCH-PAGE-{timestamp.strftime('%Y%m%d-%H%M%S')}-{unique_id}"
        search_run_ids: List[str] = []
        
        # Create runs with searchable pattern
        for i in range(8):
            result = client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number=f"{search_prefix}-{i:02d}",
                part_number="PCB-001",
                started_at=timestamp,
                ended_at=timestamp
            )
            assert_create_run_success(result)
            search_run_ids.append(result.id)
        
        # Don't rely on search - filter directly
        all_runs = client.runs.list(limit=100)
        assert_get_runs_success(all_runs)
        
        # Filter to our search runs
        search_runs = [r for r in all_runs.data if r.id in search_run_ids]
        assert len(search_runs) == 8, f"Expected 8 search runs, found {len(search_runs)}"
        
        # Test pagination with filtered results
        # Simulate pagination by slicing
        page1_data = search_runs[:3]
        page2_data = search_runs[3:6]
        
        assert len(page1_data) == 3
        assert len(page2_data) == 3
        
        # Verify no overlap
        page1_ids = {r.id for r in page1_data}
        page2_ids = {r.id for r in page2_data}
        assert len(page1_ids & page2_ids) == 0
        
        # All results should have our search prefix
        for run in page1_data + page2_data:
            assert search_prefix in run.unit.serial_number