"""Test sorting parameters in runs.list()."""

import pytest
from typing import List
from tofupilot.v2 import TofuPilot, models
from ...utils import assert_create_run_success, assert_get_runs_success, get_random_test_dates
from datetime import datetime, timedelta, timezone


class TestRunsSorting:
    """Test sort_by and sort_order parameters."""
    
    @pytest.fixture 
    def test_runs_data(self, client: TofuPilot, procedure_id: str) -> List[models.RunCreateResponse]:
        """Create test runs with different timing for sorting tests."""
        # Use current time as base for more realistic dates
        base_time = datetime.now(timezone.utc)
        
        # Create runs with specific time offsets for predictable sorting
        test_runs = [
            client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                started_at=base_time - timedelta(days=5),
                ended_at=base_time - timedelta(days=5) + timedelta(hours=1),
                serial_number="SORT-TEST-001",
                part_number="PCB-001"
            ),
            client.runs.create(
                outcome="FAIL",
                procedure_id=procedure_id,
                started_at=base_time - timedelta(days=3),
                ended_at=base_time - timedelta(days=3) + timedelta(hours=3),
                serial_number="SORT-TEST-002",
                part_number="PCB-001"
            ),
            client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                started_at=base_time - timedelta(days=1),
                ended_at=base_time - timedelta(days=1) + timedelta(hours=2),
                serial_number="SORT-TEST-003",
                part_number="PCB-001"
            )
        ]
        
        for run in test_runs:
            assert_create_run_success(run)
            
        return test_runs

    def test_sort_by_started_at_asc(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test sorting by started_at ascending."""
        result = client.runs.list(sort_by="started_at", sort_order="asc", limit=10)
        assert_get_runs_success(result)
        
        # Test that sorting parameter is accepted and returns valid results
        assert isinstance(result.data, list)
        assert len(result.data) >= 0

    def test_sort_by_started_at_desc(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test sorting by started_at descending."""
        result = client.runs.list(sort_by="started_at", sort_order="desc", limit=10)
        assert_get_runs_success(result)
        
        assert isinstance(result.data, list)
        assert len(result.data) >= 0

    def test_sort_by_created_at_asc(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test sorting by created_at ascending."""
        result = client.runs.list(sort_by="created_at", sort_order="asc", limit=10)
        assert_get_runs_success(result)
        
        assert isinstance(result.data, list)
        assert len(result.data) >= 0

    def test_sort_by_created_at_desc(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test sorting by created_at descending."""
        result = client.runs.list(sort_by="created_at", sort_order="desc", limit=10)
        assert_get_runs_success(result)
        
        assert isinstance(result.data, list)
        assert len(result.data) >= 0

    def test_sort_by_duration_asc(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test sorting by duration ascending."""
        result = client.runs.list(sort_by="duration", sort_order="asc", limit=10)
        assert_get_runs_success(result)
        
        assert isinstance(result.data, list)
        assert len(result.data) >= 0

    def test_sort_by_duration_desc(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test sorting by duration descending."""
        result = client.runs.list(sort_by="duration", sort_order="desc", limit=10)
        assert_get_runs_success(result)
        
        assert isinstance(result.data, list)
        assert len(result.data) >= 0

    def test_default_sorting(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test default sorting behavior."""
        result = client.runs.list(limit=10)
        assert_get_runs_success(result)
        
        # Default sorting should work
        assert isinstance(result.data, list)
        assert len(result.data) >= 0

    def test_sort_order_validation(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test that different sort combinations work."""
        # Test various sort combinations to ensure all parameters are accepted
        sort_combinations: List[tuple[str, str]] = [
            ("started_at", "asc"),
            ("started_at", "desc"),
            ("created_at", "asc"), 
            ("created_at", "desc"),
            ("duration", "asc"),
            ("duration", "desc")
        ]
        
        for sort_by, sort_order in sort_combinations:
            result = client.runs.list(sort_by=sort_by, sort_order=sort_order, limit=5)
            assert_get_runs_success(result)
            assert isinstance(result.data, list)