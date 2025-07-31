"""Test ID-based filtering parameters in runs.list()."""

import pytest
from typing import List
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot, models
from ...utils import assert_create_run_success, assert_get_runs_success


class TestRunsIdsFiltering:
    """Test ID-based filtering parameters."""
    
    @pytest.fixture 
    def test_runs_data(self, client: TofuPilot, procedure_id: str) -> List[models.RunCreateResponse]:
        """Create test runs for ID filtering."""
        base_time = datetime.now(timezone.utc)
        
        test_runs = [
            client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number="IDS-TEST-001",
                part_number="BOARD-001",
                started_at=base_time,
                ended_at=base_time
            ),
            client.runs.create(
                outcome="FAIL",
                procedure_id=procedure_id,
                serial_number="IDS-TEST-002",
                part_number="BOARD-002",
                started_at=base_time,
                ended_at=base_time
            ),
            client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number="IDS-TEST-003",
                part_number="SENSOR-001",
                started_at=base_time,
                ended_at=base_time
            )
        ]
        
        for run in test_runs:
            assert_create_run_success(run)
            
        return test_runs

    def test_filter_by_single_id(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test filtering by single run ID."""
        target_id = test_runs_data[0].id
        
        result = client.runs.list(ids=[target_id])
        assert_get_runs_success(result)
        
        found_ids = [run.id for run in result.data]
        assert target_id in found_ids

    def test_filter_by_multiple_ids(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test filtering by multiple run IDs."""
        target_ids = [test_runs_data[0].id, test_runs_data[1].id]
        
        result = client.runs.list(ids=target_ids)
        assert_get_runs_success(result)
        
        found_ids = [run.id for run in result.data]
        
        for target_id in target_ids:
            assert target_id in found_ids

    def test_filter_by_serial_numbers(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test filtering by serial numbers."""
        result = client.runs.list(serial_numbers=["IDS-TEST-001", "IDS-TEST-003"])
        assert_get_runs_success(result)
        
        test_run_ids = {run.id for run in test_runs_data}
        our_runs = [run for run in result.data if run.id in test_run_ids]
        
        assert len(our_runs) >= 2

    def test_filter_by_part_numbers(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test filtering by part numbers."""
        result = client.runs.list(part_numbers=["BOARD-001", "SENSOR-001"])
        assert_get_runs_success(result)
        
        test_run_ids = {run.id for run in test_runs_data}
        our_runs = [run for run in result.data if run.id in test_run_ids]
        
        assert len(our_runs) >= 2

    def test_filter_by_procedure_ids(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse], procedure_id: str):
        """Test filtering by procedure IDs."""
        result = client.runs.list(procedure_ids=[procedure_id])
        assert_get_runs_success(result)
        
        test_run_ids = {run.id for run in test_runs_data}
        our_runs = [run for run in result.data if run.id in test_run_ids]
        
        assert len(our_runs) >= len(test_runs_data)

    def test_filter_by_procedure_versions(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test filtering by procedure versions."""
        # Test with a common version pattern
        result = client.runs.list(procedure_versions=["1.0", "1.0.0", "latest"])
        assert_get_runs_success(result)
        
        # Should get some results (may or may not include our test runs)
        assert isinstance(result.data, list)

    def test_filter_by_revision_numbers(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test filtering by revision numbers."""
        # Test with common revision patterns
        result = client.runs.list(revision_numbers=["1", "1.0", "A1", "REV-001"])
        assert_get_runs_success(result)
        
        # Should get some results (may or may not include our test runs)
        assert isinstance(result.data, list)

    def test_empty_ids_filter(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test empty IDs array behavior.
        
        Empty array should be equivalent to no filter (return all runs).
        This is the correct behavior: ids=[] means "don't filter by IDs".
        """
        result_empty = client.runs.list(ids=[])
        result_no_param = client.runs.list()
        assert_get_runs_success(result_empty)
        assert_get_runs_success(result_no_param)
        
        # Empty array should behave same as no parameter
        assert len(result_empty.data) > 0
        assert len(result_empty.data) == len(result_no_param.data)

    def test_empty_procedure_versions_filter(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test empty procedure_versions array behavior."""
        result_empty = client.runs.list(procedure_versions=[])
        result_no_param = client.runs.list()
        assert_get_runs_success(result_empty)
        assert_get_runs_success(result_no_param)
        
        # Empty array should behave same as no parameter
        assert len(result_empty.data) > 0
        assert len(result_empty.data) == len(result_no_param.data)

    def test_empty_revision_numbers_filter(self, client: TofuPilot, test_runs_data: List[models.RunCreateResponse]):
        """Test empty revision_numbers array behavior."""
        result_empty = client.runs.list(revision_numbers=[])
        result_no_param = client.runs.list()
        assert_get_runs_success(result_empty)
        assert_get_runs_success(result_no_param)
        
        # Empty array should behave same as no parameter  
        assert len(result_empty.data) > 0
        assert len(result_empty.data) == len(result_no_param.data)