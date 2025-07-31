"""Test procedure list pagination."""

import pytest
from typing import List
from datetime import datetime, timezone
import uuid
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_procedure_success, assert_get_procedures_success
from ...utils import assert_station_access_forbidden


class TestProceduresPagination:
    """Test pagination in procedures.list()."""
    
    @pytest.fixture
    def test_procedures_for_pagination(self, client: TofuPilot, auth_type: str) -> List[models.ProcedureCreateResponse]:
        """Create test procedures for pagination tests."""
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name="STATION-PAGINATION-FAIL")
            
            # Return empty list since station can't create procedures
            return []
            
        # User API can create procedures
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        test_procedures: List[models.ProcedureCreateResponse] = []
        # Create 15 procedures to test pagination
        for i in range(15):
            procedure = client.procedures.create(
                name=f"PAGE-TEST-{timestamp}-{unique_id}-{i:03d}"
            )
            assert_create_procedure_success(procedure)
            test_procedures.append(procedure)
            
        return test_procedures

    def test_default_limit(self, client: TofuPilot) -> None:
        """Test default limit of 50 items."""
        result = client.procedures.list()
        assert_get_procedures_success(result)
        
        # Should return at most 50 items (default limit)
        assert len(result.data) <= 50
    
    def test_custom_limit(self, client: TofuPilot, test_procedures_for_pagination: List[models.ProcedureCreateResponse], auth_type: str) -> None:
        """Test custom limit parameter."""
        if auth_type == "station":
            # Station can't create procedures, just test basic pagination
            result = client.procedures.list(limit=5)
            assert_get_procedures_success(result)
            assert len(result.data) <= 5
            return
        
        # Ensure we have test procedures created
        assert len(test_procedures_for_pagination) >= 15, "Test procedures should be created"
        
        # Test with limit of 5
        result = client.procedures.list(limit=5)
        assert_get_procedures_success(result)
        
        # Should return exactly 5 items
        assert len(result.data) == 5
        
        # Since we created 15+ procedures, has_more should be True
        assert result.meta.has_more is True
        assert result.meta.next_cursor is not None

    def test_limit_validation(self, client: TofuPilot) -> None:
        """Test limit parameter validation."""
        # Test limit too small
        with pytest.raises(Exception) as exc_info:
            client.procedures.list(limit=0)
        assert "limit" in str(exc_info.value).lower()
        
        # Test limit too large
        with pytest.raises(Exception) as exc_info:
            client.procedures.list(limit=101)
        assert "limit" in str(exc_info.value).lower()
        
        # Test valid edge cases
        result = client.procedures.list(limit=1)
        assert_get_procedures_success(result)
        assert len(result.data) <= 1
        
        result = client.procedures.list(limit=100)
        assert_get_procedures_success(result)
        assert len(result.data) <= 100

    def test_cursor_pagination(self, client: TofuPilot, test_procedures_for_pagination: List[models.ProcedureCreateResponse], auth_type: str) -> None:
        """Test cursor-based pagination."""
        if auth_type == "station":
            # Station can't create procedures, just test basic pagination
            page1 = client.procedures.list(limit=3)
            assert_get_procedures_success(page1)
            
            if page1.meta.has_more:
                page2 = client.procedures.list(limit=3, cursor=page1.meta.next_cursor)
                assert_get_procedures_success(page2)
                
                # Verify no overlap between pages
                page1_ids = {p.id for p in page1.data}
                page2_ids = {p.id for p in page2.data}
                assert len(page1_ids & page2_ids) == 0
            return
            
        # Ensure we have test procedures created
        assert len(test_procedures_for_pagination) >= 15, "Test procedures should be created"
        
        # Get first page with limit 5
        page1 = client.procedures.list(limit=5)
        assert_get_procedures_success(page1)
        assert len(page1.data) == 5
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None
        
        # Get second page using cursor
        page2 = client.procedures.list(limit=5, cursor=page1.meta.next_cursor)
        assert_get_procedures_success(page2)
        assert len(page2.data) == 5
        
        # Verify no overlap between pages
        page1_ids = {p.id for p in page1.data}
        page2_ids = {p.id for p in page2.data}
        assert len(page1_ids & page2_ids) == 0  # No intersection
        
        # Get third page
        if page2.meta.has_more:
            page3 = client.procedures.list(limit=5, cursor=page2.meta.next_cursor)
            assert_get_procedures_success(page3)
            
            # Should have remaining procedures (up to 5)
            assert len(page3.data) <= 5
            
            # No overlap with previous pages
            page3_ids = {p.id for p in page3.data}
            assert len(page1_ids & page3_ids) == 0
            assert len(page2_ids & page3_ids) == 0

    def test_last_page_has_more_false(self, client: TofuPilot) -> None:
        """Test that last page has has_more=False."""
        # Get all procedures with a large limit
        all_procedures = client.procedures.list(limit=100)
        assert_get_procedures_success(all_procedures)
        total_count = len(all_procedures.data)
        
        if total_count < 100:
            # If we got all procedures in one page, has_more should be False
            assert all_procedures.meta.has_more is False
            assert all_procedures.meta.next_cursor is None
        else:
            # Navigate to last page
            page_size = 10
            cursor = all_procedures.meta.next_cursor
            last_page = None
            page_count = 0
            max_pages = 20  # Prevent infinite loop
            
            while cursor and page_count < max_pages:
                page = client.procedures.list(limit=page_size, cursor=cursor)
                assert_get_procedures_success(page)
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
                assert all_procedures.meta.has_more is True
    
    def test_cursor_consistency(self, client: TofuPilot, test_procedures_for_pagination: List[models.ProcedureCreateResponse], auth_type: str) -> None:
        """Test that cursor returns consistent results."""
        if auth_type == "station":
            # Station can't create procedures, just test basic consistency
            page1 = client.procedures.list(limit=3)
            assert_get_procedures_success(page1)
            
            if page1.meta.has_more:
                cursor = page1.meta.next_cursor
                
                # Get the same page multiple times
                page2a = client.procedures.list(limit=3, cursor=cursor)
                page2b = client.procedures.list(limit=3, cursor=cursor)
                
                assert_get_procedures_success(page2a)
                assert_get_procedures_success(page2b)
                
                # Should return the same data
                assert len(page2a.data) == len(page2b.data)
                for i in range(len(page2a.data)):
                    assert page2a.data[i].id == page2b.data[i].id
            return
        
        # Ensure we have test procedures created
        assert len(test_procedures_for_pagination) >= 15, "Test procedures should be created"
        
        # Get a page with cursor
        page1 = client.procedures.list(limit=3)
        assert_get_procedures_success(page1)
        
        if page1.meta.has_more:
            cursor = page1.meta.next_cursor
            
            # Get the same page multiple times
            page2a = client.procedures.list(limit=3, cursor=cursor)
            page2b = client.procedures.list(limit=3, cursor=cursor)
            
            assert_get_procedures_success(page2a)
            assert_get_procedures_success(page2b)
            
            # Should return the same data
            assert len(page2a.data) == len(page2b.data)
            for i in range(len(page2a.data)):
                assert page2a.data[i].id == page2b.data[i].id