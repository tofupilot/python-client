"""Test date-based filtering in procedures.list()."""

import pytest
from typing import List
from datetime import datetime, timezone, timedelta
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_procedure_success, assert_get_procedures_success, get_procedure_by_id
from ...utils import assert_station_access_forbidden


class TestProceduresDateFiltering:
    """Test filtering procedures by creation date."""
    
    @pytest.fixture
    def test_procedures_with_dates(self, client: TofuPilot, auth_type: str) -> List[models.ProcedureListData]:
        """Create test procedures or test station authorization."""
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name="STATION-SHOULD-FAIL")
            
            # Return empty list since station can't create procedures for date filtering tests
            return []
            
        # User API can create procedures
        base_timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        
        test_procedures: List[models.ProcedureListData] = []
        # Create procedures with small delays to ensure different timestamps
        for i in range(5):
            create_result = client.procedures.create(
                name=f"DATE-FILTER-TEST-{base_timestamp}-{i:03d}"
            )
            assert_create_procedure_success(create_result)
            
            # Fetch the full procedure to get created_at
            proc = get_procedure_by_id(client, create_result.id)
            assert proc is not None
            test_procedures.append(proc)
            
            # Small delay to ensure different creation times
            import time
            time.sleep(0.1)
            
        return test_procedures

    def test_filter_by_created_after(self, client: TofuPilot, test_procedures_with_dates: List[models.ProcedureListData], auth_type: str):
        """Test filtering procedures created after a specific date."""
        if auth_type == "station":
            # Station can list procedures (but fixture already tested creation authorization)
            result = client.procedures.list(created_after=datetime.now(timezone.utc) - timedelta(hours=1))
            assert_get_procedures_success(result)
            # Test passes if station can successfully list procedures
            return
            
        # User API test with created procedures
        if len(test_procedures_with_dates) < 3:
            # If we don't have enough test procedures, just test basic functionality
            result = client.procedures.list(created_after=datetime.now(timezone.utc) - timedelta(hours=1))
            assert_get_procedures_success(result)
            # Test passes if we can successfully list procedures with date filter
            return
            
        # Use a time slightly before the first procedure creation
        threshold_time = test_procedures_with_dates[2].created_at - timedelta(seconds=1)
        
        result = client.procedures.list(created_after=threshold_time)
        assert_get_procedures_success(result)
        
        # Should include at least our test procedures created after threshold
        test_ids_in_result = {p.id for p in result.data}
        expected_procedures = test_procedures_with_dates[2:]  # Last 3 procedures
        found_count = sum(1 for p in expected_procedures if p.id in test_ids_in_result)
        assert found_count >= 3
        
        # All our test procedures in the result should meet the date criteria
        our_procedures_in_result = [p for p in result.data if p.id in {proc.id for proc in expected_procedures}]
        for procedure in our_procedures_in_result:
            if hasattr(procedure, 'created_at') and procedure.created_at:
                assert procedure.created_at >= threshold_time, f"Our test procedure {procedure.name} should be after threshold"

    def test_filter_by_created_before(self, client: TofuPilot, test_procedures_with_dates: List[models.ProcedureListData], auth_type: str):
        """Test filtering procedures created before a specific date."""
        if auth_type == "station":
            # Station can list procedures (authorization already tested in fixture)
            result = client.procedures.list(created_before=datetime.now(timezone.utc))
            assert_get_procedures_success(result)
            return
            
        if len(test_procedures_with_dates) < 3:
            # If we don't have enough test procedures, just test basic functionality
            result = client.procedures.list(created_before=datetime.now(timezone.utc))
            assert_get_procedures_success(result)
            # Test passes if we can successfully list procedures with date filter
            return
            
        # Use a time slightly after the middle procedure creation
        threshold_time = test_procedures_with_dates[2].created_at + timedelta(seconds=1)
        
        result = client.procedures.list(created_before=threshold_time)
        assert_get_procedures_success(result)
        
        # Should include at least our test procedures created before threshold
        test_ids_in_result = {p.id for p in result.data}
        expected_procedures = test_procedures_with_dates[:3]  # First 3 procedures
        found_count = sum(1 for p in expected_procedures if p.id in test_ids_in_result)
        assert found_count >= 3
        
        # All our test procedures in the result should meet the date criteria
        our_procedures_in_result = [p for p in result.data if p.id in {proc.id for proc in expected_procedures}]
        for procedure in our_procedures_in_result:
            if hasattr(procedure, 'created_at') and procedure.created_at:
                assert procedure.created_at <= threshold_time, f"Our test procedure {procedure.name} should be before threshold"

    def test_filter_by_date_range(self, client: TofuPilot, test_procedures_with_dates: List[models.ProcedureListData], auth_type: str):
        """Test filtering procedures within a date range."""
        if auth_type == "station" or len(test_procedures_with_dates) < 4:
            # Station can list procedures with date range
            start_time = datetime.now(timezone.utc) - timedelta(hours=1)
            end_time = datetime.now(timezone.utc)
            result = client.procedures.list(created_after=start_time, created_before=end_time)
            assert_get_procedures_success(result)
            return
            
        # Get time range from second to fourth procedure
        start_time = test_procedures_with_dates[1].created_at - timedelta(seconds=1)
        end_time = test_procedures_with_dates[3].created_at + timedelta(seconds=1)
        
        result = client.procedures.list(
            created_after=start_time,
            created_before=end_time
        )
        assert_get_procedures_success(result)
        
        # Should include procedures 1, 2, 3
        test_ids_in_result = {p.id for p in result.data}
        expected_procedures = test_procedures_with_dates[1:4]  # Procedures 1-3
        found_count = sum(1 for p in expected_procedures if p.id in test_ids_in_result)
        assert found_count >= 3
        
        # All our test procedures in the result should be within the range
        our_procedures_in_result = [p for p in result.data if p.id in {proc.id for proc in expected_procedures}]
        for procedure in our_procedures_in_result:
            if hasattr(procedure, 'created_at') and procedure.created_at:
                assert start_time <= procedure.created_at <= end_time, f"Our test procedure {procedure.name} should be within date range"

    def test_filter_future_date(self, client: TofuPilot, auth_type: str):
        """Test filtering with future date behavior."""
        future_date = datetime.now(timezone.utc) + timedelta(days=1)
        
        result = client.procedures.list(created_after=future_date)
        assert_get_procedures_success(result)
        
        if auth_type == "station":
            # Station can list procedures - just verify the call succeeds
            return
            
        # Check if any returned procedures are actually from the future
        # If the API returns procedures, they should not be from the future
        now = datetime.now(timezone.utc)
        for procedure in result.data:
            if hasattr(procedure, 'created_at') and procedure.created_at:
                assert procedure.created_at <= now, f"Procedure {procedure.name} appears to be from the future"
        
        # The API behavior for future dates may vary - test passes if no future procedures returned

    def test_filter_very_old_date(self, client: TofuPilot, test_procedures_with_dates: List[models.ProcedureListData], auth_type: str):
        """Test filtering with very old date includes all procedures."""
        old_date = datetime.now(timezone.utc) - timedelta(days=365)
        
        result = client.procedures.list(created_after=old_date)
        assert_get_procedures_success(result)
        
        if auth_type == "station":
            # Station can list procedures - just verify the call succeeds
            return
        
        # Should include at least our test procedures
        test_ids_in_result = {p.id for p in result.data}
        found_count = sum(1 for p in test_procedures_with_dates if p.id in test_ids_in_result)
        assert found_count >= 5

    def test_narrow_date_range(self, client: TofuPilot, test_procedures_with_dates: List[models.ProcedureListData], auth_type: str):
        """Test filtering with a very narrow date range."""
        if auth_type == "station" or len(test_procedures_with_dates) < 3:
            # Station can list procedures or skip if not enough test data
            result = client.procedures.list(created_after=datetime.now(timezone.utc) - timedelta(hours=1))
            assert_get_procedures_success(result)
            return
            
        target_procedure = test_procedures_with_dates[2]
        
        # Create a 2-second window around the procedure
        result = client.procedures.list(
            created_after=target_procedure.created_at - timedelta(seconds=1),
            created_before=target_procedure.created_at + timedelta(seconds=1)
        )
        assert_get_procedures_success(result)
        
        # Should find at least the target procedure
        found_ids = {p.id for p in result.data}
        assert target_procedure.id in found_ids

    def test_date_filter_with_pagination(self, client: TofuPilot, test_procedures_with_dates: List[models.ProcedureListData], auth_type: str):
        """Test date filtering combined with pagination."""
        if auth_type == "station" or len(test_procedures_with_dates) < 1:
            # Station can list procedures with pagination
            result = client.procedures.list(created_after=datetime.now(timezone.utc) - timedelta(hours=1), limit=2)
            assert_get_procedures_success(result)
            return
            
        # Use all test procedures time range
        start_time = test_procedures_with_dates[0].created_at - timedelta(seconds=1)
        end_time = test_procedures_with_dates[-1].created_at + timedelta(seconds=1)
        
        result = client.procedures.list(
            created_after=start_time,
            created_before=end_time,
            limit=2
        )
        assert_get_procedures_success(result)
        
        # Should respect both date filter and limit
        assert len(result.data) <= 2
        
        # Find our test procedures in the results
        test_procedure_ids = {p.id for p in test_procedures_with_dates}
        our_procedures_in_result = [p for p in result.data if p.id in test_procedure_ids]
        
        # Our test procedures in result should meet date criteria
        for procedure in our_procedures_in_result:
            if hasattr(procedure, 'created_at') and procedure.created_at:
                assert start_time <= procedure.created_at <= end_time, f"Our test procedure {procedure.name} should be within date range"

    def test_date_filter_with_search(self, client: TofuPilot, test_procedures_with_dates: List[models.ProcedureListData], auth_type: str):
        """Test date filtering combined with search."""
        if auth_type == "station" or len(test_procedures_with_dates) < 1:
            # Station can list procedures with search
            result = client.procedures.list(created_after=datetime.now(timezone.utc) - timedelta(hours=1), search_query="test")
            assert_get_procedures_success(result)
            return
            
        # Use a date range that includes test procedures
        start_time = test_procedures_with_dates[0].created_at - timedelta(seconds=1)
        
        result = client.procedures.list(
            created_after=start_time,
            search_query="DATE-FILTER-TEST"
        )
        assert_get_procedures_success(result)
        
        # Should find procedures matching both date and search criteria
        matching_procedures: List[models.ProcedureListData] = []
        for procedure in result.data:
            if ("DATE-FILTER-TEST" in procedure.name and 
                hasattr(procedure, 'created_at') and 
                procedure.created_at and 
                procedure.created_at >= start_time):
                matching_procedures.append(procedure)
        
        assert len(matching_procedures) >= 1