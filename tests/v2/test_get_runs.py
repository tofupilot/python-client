"""
Test get_runs functionality against local TofuPilot server running on localhost:3000.

This test is designed to run against a local development instance of TofuPilot.
It requires:
1. TofuPilot server running on http://localhost:3000
2. Valid API key set in TOFUPILOT_API_KEY environment variable
3. Network connectivity to localhost
4. TODO: Existing runs and procedures in the database for comprehensive testing
"""

import pytest
from datetime import datetime, timedelta
from typing import Literal, List

from tofupilot.client import TofuPilotClient
from .utils import client, assert_get_runs_success
from tofupilot.models.models import (
    Phase,
    Measurement,
    Log,
    PhaseOutcome,
    MeasurementOutcome,
    LogLevel,
    SubUnit
)


class TestGetRuns:

    @pytest.fixture(params=["PASS", "FAIL"])
    def outcome_to_test(self, request) -> Literal["PASS", "FAIL"]:
        """Test different run outcomes."""
        return request.param
    
    all_exclude_options = ["createdBy", "procedure", "unit", "phases", "procedureVersion", "attachments", "measurements", "logs"]

    @pytest.fixture(params=[
        ["createdBy"],
        ["procedure"],
        ["unit"],
        ["phases"],
        ["measurements"],
        ["logs"],
        ["createdBy", "unit"],
        ["procedure", "phases", "measurements", "logs"],
        all_exclude_options,
    ])
    def exclude_options(self, request) -> List[Literal["createdBy", "procedure", "unit", "phases", "measurements", "logs"]]:
        """Test different field exclusion options."""
        return request.param
    
    @pytest.fixture(params=[
        "-startedAt",
    	"startedAt",
    	"-createdAt",
    	"createdAt",
    	"-duration",
    	"duration",
    ])
    def sort_option(self, request):
        """Different sorting options."""
        return request.param

    def test_no_parameters(self, client: TofuPilotClient):
        """Test getting all runs with no filters."""
        result = client.get_runs()
        assert_get_runs_success(result)

    def test_by_procedure_id(self, client: TofuPilotClient, procedure_id):
        """Test filtering runs by procedure ID."""
        result = client.get_runs(procedureIds=[procedure_id])
        assert_get_runs_success(result)
        # Verify all returned runs belong to the specified procedure
        for run in result["data"]:
            assert "procedure" in run
            assert run["procedure"]

            assert run["procedure"]["id"] == procedure_id, "Run filtered by procedure id does not have that procedure id"

    def test_by_multiple_procedure_ids(self, client: TofuPilotClient, procedure_id):
        """Test filtering runs by multiple procedure IDs."""
        # Use the same procedure ID twice to ensure the array parameter works
        result = client.get_runs(procedureIds=[procedure_id, procedure_id])
        assert_get_runs_success(result)

    def test_by_outcome(self, client: TofuPilotClient, outcome_to_test):
        """Test filtering runs by outcome."""
        result = client.get_runs(outcome=outcome_to_test)
        assert_get_runs_success(result)
        # Verify all returned runs have the specified outcome
        for run in result["data"]:
            assert run.get("outcome") == outcome_to_test

    def test_pagination_with_limit(self, client: TofuPilotClient):
        """Test pagination using limit parameter."""
        # Test small limit
        result = client.get_runs(limit=5)
        assert_get_runs_success(result)
        assert len(result["data"]) <= 5

    def test_pagination_with_offset(self, client: TofuPilotClient):
        """Test pagination using offset parameter."""
        # Get first batch
        first_batch = client.get_runs(limit=3, offset=0)
        assert_get_runs_success(first_batch)
        # Get second batch
        second_batch = client.get_runs(limit=3, offset=3)
        assert_get_runs_success(second_batch)
        
        # If both batches have data, they should be different
        if first_batch["data"] and second_batch["data"]:
            first_ids = {run["id"] for run in first_batch["data"]}
            second_ids = {run["id"] for run in second_batch["data"]}
            assert first_ids.isdisjoint(second_ids), "Paginated results should not overlap"

    def test_sorting(self, client: TofuPilotClient, sort_option):
        """Test different sorting options."""
        sort_key = sort_option.removeprefix("-")

        result = client.get_runs(sort=sort_option, limit=10)
        assert_get_runs_success(result)
        
        if sort_key != "duration":
            elems = result["data"]
            if (len(elems) >= 2):
                previous = elems[0]
                assert sort_key in previous

                for elem in elems:
                    assert sort_key in elem
                    if sort_option.startswith("-"):
                        assert previous[sort_key] >= elem[sort_key]
                    else:
                        assert previous[sort_key] <= elem[sort_key]

                    previous = elem

            

    def test_exclude_fields(self, client: TofuPilotClient, exclude_options):
        """Test excluding specific fields from response."""
        result = client.get_runs(exclude=exclude_options, limit=5)
        assert_get_runs_success(result)
        
        # Verify excluded fields are not present in the response
        for run in result["data"]:
            for excluded_field in exclude_options:

                assert excluded_field not in run, \
                    f"Excluded field '{excluded_field}' should not be present"
    
    def test_exclude_all(self, client: TofuPilotClient):
        
        result = client.get_runs(exclude=["all"])
        assert_get_runs_success(result)

        # Verify excluded fields are not present in the response
        for run in result["data"]:
            for excluded_field in self.all_exclude_options:
                
                assert excluded_field not in run, \
                    f"Excluded field '{excluded_field}' should not be present"

    def test_complex_filter_combination(self, client: TofuPilotClient, procedure_id):
        """Test combining multiple filters."""
        result = client.get_runs(
            procedureIds=[procedure_id],
            outcome="PASS",
            limit=10,
            sort="-startedAt",
            exclude=["logs", "measurements"]
        )
        assert_get_runs_success(result)
        
        # Verify filters are applied
        for run in result["data"]:
            # Check outcome filter
            if "outcome" in run:
                assert run["outcome"] == "PASS"
            
            # Check procedure filter (if procedure data is included)
            if "procedure" in run and run["procedure"]:
                assert run["procedure"]["id"] == procedure_id
            
            # Check excluded fields
            assert "logs" not in run or run["logs"] is None
            assert "measurements" not in run or run["measurements"] is None

    def test_no_limit(self, client: TofuPilotClient):
        """Test getting all runs with no limit."""
        result = client.get_runs(limit=-1)
        assert_get_runs_success(result)
        # Should return all available runs (could be many)
        # TODO: Test that all runs are returned

    def test_by_unit_serial_number(self, client: TofuPilotClient):
        """Test filtering runs by unit serial number."""
        # Test with a test serial number that might exist in the database
        test_serial_number = "TEST-UNIT-001"
        
        result = client.get_runs(unitSerialNumbers=[test_serial_number])
        assert_get_runs_success(result)
        
        # Verify all returned runs belong to units with the specified serial number
        for run in result["data"]:
            if "unit" in run and run["unit"]:
                unit = run["unit"]
                if "serialNumber" in unit:
                    assert unit["serialNumber"] == test_serial_number

    def test_by_multiple_unit_serial_numbers(self, client: TofuPilotClient):
        """Test filtering runs by multiple unit serial numbers."""
        # Test with multiple serial numbers
        serial_numbers = ["TEST-UNIT-001", "TEST-UNIT-002"]
        
        result = client.get_runs(unitSerialNumbers=serial_numbers)
        assert_get_runs_success(result)
        
        # Verify all returned runs belong to units with one of the specified serial numbers
        for run in result["data"]:
            if "unit" in run and run["unit"]:
                unit = run["unit"]
                if "serialNumber" in unit:
                    assert unit["serialNumber"] in serial_numbers

    def test_empty_filters(self, client: TofuPilotClient):
        """Test with empty filter lists."""
        result = client.get_runs(
            procedureIds=[],
            unitSerialNumbers=[],
            ids=[]
        )
        assert_get_runs_success(result)
        # Empty filters should return all runs (up to default limit)

    def test_response_structure(self, client: TofuPilotClient):
        """Test that response has expected structure."""
        result = client.get_runs(limit=1)
        assert_get_runs_success(result)
        
        # Check top-level structure
        assert isinstance(result, dict)
        
        # Check run structure if data exists
        if result["data"]:
            run = result["data"][0]
            assert isinstance(run, dict)
            assert "id" in run
            assert isinstance(run["id"], str)

            # TODO: More complete test
            
            # These fields should typically be present
            expected_fields = ["createdAt", "outcome"]
            for field in expected_fields:
                if field in run:
                    assert run[field] is not None
