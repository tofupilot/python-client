"""Test search_query parameter in runs.list()."""

import pytest
from typing import List
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot, models
from ...utils import assert_create_run_success, assert_get_runs_success


class TestRunsSearchFiltering:
    """Test search_query parameter."""
    
    @pytest.fixture 
    def test_runs_data(self, client: TofuPilot, procedure_id: str) -> List[models.RunCreateResponse]:
        """Create test runs with specific searchable characteristics."""
        base_time = datetime.now(timezone.utc)
        
        test_runs = [
            client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number="SEARCH-ALPHA-001",
                part_number="BOARD-ALPHA-V1",
                started_at=base_time,
                ended_at=base_time
            ),
            client.runs.create(
                outcome="FAIL",
                procedure_id=procedure_id,
                serial_number="SEARCH-BETA-002",
                part_number="BOARD-BETA-V2",
                started_at=base_time,
                ended_at=base_time
            ),
            client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number="UNIQUE-GAMMA-003",
                part_number="SENSOR-GAMMA-V1",
                started_at=base_time,
                ended_at=base_time
            )
        ]
        
        for run in test_runs:
            assert_create_run_success(run)
            
        return test_runs

    def test_search_by_serial_number_full(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test searching by full serial number."""
        result = client.runs.list(search_query="SEARCH-ALPHA-001")
        assert_get_runs_success(result)
        
        test_run_ids = {run.id for run in test_runs_data}
        our_runs = [run for run in result.data if run.id in test_run_ids]
        
        assert len(our_runs) >= 1

    def test_search_by_serial_number_partial(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test searching by partial serial number."""
        result = client.runs.list(search_query="SEARCH-")
        assert_get_runs_success(result)
        
        test_run_ids = {run.id for run in test_runs_data}
        our_runs = [run for run in result.data if run.id in test_run_ids]
        
        assert len(our_runs) >= 2

    def test_search_by_part_number(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test that part number search is no longer supported (optimized out)."""
        # Search by part number should not find runs by part info
        result = client.runs.list(search_query="BOARD-ALPHA-V1")
        assert_get_runs_success(result)
        
        # Part number search is no longer supported, so we don't expect to find our test runs
        test_run_ids = {run.id for run in test_runs_data}
        our_runs = [run for run in result.data if run.id in test_run_ids]
        
        # Changed assertion - we don't expect to find runs by part number anymore
        assert len(our_runs) == 0

    def test_search_by_run_id(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test searching by run ID."""
        target_id = test_runs_data[0].id
        
        result = client.runs.list(search_query=target_id)
        assert_get_runs_success(result)
        
        found_ids = [run.id for run in result.data]
        assert target_id in found_ids

    def test_search_case_insensitive(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test case insensitive search."""
        result = client.runs.list(search_query="alpha")
        assert_get_runs_success(result)
        
        test_run_ids = {run.id for run in test_runs_data}
        our_runs = [run for run in result.data if run.id in test_run_ids]
        
        assert len(our_runs) >= 1

    def test_search_no_results(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test search that returns no results."""
        result = client.runs.list(search_query="IMPOSSIBLE-NONEXISTENT-TERM")
        assert_get_runs_success(result)
        
        test_run_ids = {run.id for run in test_runs_data}
        our_runs = [run for run in result.data if run.id in test_run_ids]
        
        assert len(our_runs) == 0