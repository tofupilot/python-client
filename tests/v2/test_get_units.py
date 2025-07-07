"""
Test get_units functionality against local TofuPilot server running on localhost:3000.

This test is designed to run against a local development instance of TofuPilot.
It requires:
1. TofuPilot server running on http://localhost:3000
2. Valid API key set in TOFUPILOT_API_KEY environment variable
3. Network connectivity to localhost
"""

import pytest
from typing import Literal, List

from tofupilot.client import TofuPilotClient
from .utils import client, assert_get_units_success


class TestGetUnits:

    @pytest.fixture(params=[
        "-createdAt",
        "createdAt",
        "-serialNumber",
        "serialNumber",
    ])
    def sort_option(self, request):
        """Different sorting options."""
        return request.param

    all_exclude_options = ["batch", "parent", "createdFrom", "revision", "parentChanges", "children", "runs", "createdBy"]
    @pytest.fixture(params=[
        ["createdBy"],
        ["runs"],
        ["createdBy", "runs"],
        all_exclude_options,
    ])
    def exclude_options(self, request) -> List[str]:
        """Test different field exclusion options."""
        return request.param

    def test_no_parameters(self, client: TofuPilotClient):
        """Test getting all units with no filters."""
        result = client._get_units()
        assert_get_units_success(result)

    def test_with_limit(self, client: TofuPilotClient):
        """Test pagination using limit parameter."""
        result = client._get_units(limit=5)
        assert_get_units_success(result)
        assert len(result["data"]) <= 5

    def test_with_offset(self, client: TofuPilotClient):
        """Test pagination using offset parameter."""
        # Get first batch
        first_batch = client._get_units(limit=3, offset=0)
        assert_get_units_success(first_batch)
        
        # Get second batch
        second_batch = client._get_units(limit=3, offset=3)
        assert_get_units_success(second_batch)
        
        # If both batches have data, they should be different
        if first_batch["data"] and second_batch["data"]:
            first_ids = {unit["id"] for unit in first_batch["data"]}
            second_ids = {unit["id"] for unit in second_batch["data"]}
            assert first_ids.isdisjoint(second_ids), "Paginated results should not overlap"

    def test_response_structure(self, client: TofuPilotClient):
        """Test that response has expected structure."""
        result = client._get_units(limit=1)
        assert_get_units_success(result)
        
        # Skip test if no units exist
        if not result["data"]:
            pytest.skip("No units available for testing")
        
        # Check unit structure
        unit = result["data"][0]
        assert isinstance(unit, dict)
        assert "id" in unit
        assert isinstance(unit["id"], str)
        
        # These fields should typically be present
        assert "serialNumber" in unit
        assert unit["serialNumber"] is not None
        
        # Check if partNumber exists in revision.component
        if (unit.get("revision") and 
            unit["revision"].get("component") and 
            unit["revision"]["component"].get("partNumber")):
            assert unit["revision"]["component"]["partNumber"] is not None

    def test_no_limit(self, client: TofuPilotClient):
        """Test getting all units with no limit."""
        result = client._get_units(limit=-1)
        assert_get_units_success(result)
        # Should return all available units (could be many)

    def test_by_serial_numbers(self, client: TofuPilotClient):
        """Test filtering units by serial numbers."""
        # First get some units to get actual serial numbers
        all_units = client._get_units(limit=1)
        assert_get_units_success(all_units)
        
        # Skip test if no units exist
        if not all_units["data"]:
            pytest.skip("No units available for testing")
            
        # Use the first unit's serial number for filtering
        test_serial = all_units["data"][0]["serialNumber"]
        result = client._get_units(serialNumbers=[test_serial])
        assert_get_units_success(result)
        
        # Verify all returned units have the specified serial number
        for unit in result["data"]:
            assert unit["serialNumber"] == test_serial

    def test_by_multiple_serial_numbers(self, client: TofuPilotClient):
        """Test filtering units by multiple serial numbers."""
        # Get some units first
        all_units = client._get_units(limit=3)
        assert_get_units_success(all_units)
        
        if len(all_units["data"]) < 2:
            pytest.skip("Not enough units available for testing")
            
        serial_numbers = [unit["serialNumber"] for unit in all_units["data"][:2]]
        result = client._get_units(serialNumbers=serial_numbers)
        assert_get_units_success(result)
        
        # Verify all returned units have one of the specified serial numbers
        returned_serials = {unit["serialNumber"] for unit in result["data"]}
        expected_serials = set(serial_numbers)
        assert returned_serials.issubset(expected_serials)

    def test_by_part_numbers(self, client: TofuPilotClient):
        """Test filtering units by part numbers."""
        # First get some units to find one with part number
        all_units = client._get_units(limit=10)
        assert_get_units_success(all_units)
        
        # Find a unit with revision.component.partNumber
        test_part_number = None
        for unit in all_units["data"]:
            if (unit.get("revision") and 
                unit["revision"].get("component") and 
                unit["revision"]["component"].get("partNumber")):
                test_part_number = unit["revision"]["component"]["partNumber"]
                break
        
        # Skip test if no units with part numbers found
        if not test_part_number:
            pytest.skip("No units with part numbers available for testing")
            
        # Filter by the found part number
        result = client._get_units(partNumbers=[test_part_number])
        assert_get_units_success(result)
        
        # Verify all returned units have the specified part number
        for unit in result["data"]:
            assert (unit.get("revision") and 
                   unit["revision"].get("component") and 
                   unit["revision"]["component"].get("partNumber") == test_part_number)

    def test_sorting(self, client: TofuPilotClient, sort_option):
        """Test different sorting options."""
        sort_key = sort_option.removeprefix("-")
        
        result = client._get_units(sort=sort_option, limit=10)
        assert_get_units_success(result)
        
        # Verify sorting if we have multiple results
        if len(result["data"]) >= 2:
            previous = result["data"][0]
            assert sort_key in previous
            
            for unit in result["data"]:
                assert sort_key in unit
                if sort_option.startswith("-"):
                    assert previous[sort_key] >= unit[sort_key]
                else:
                    assert previous[sort_key] <= unit[sort_key]
                previous = unit

    def test_exclude_fields(self, client: TofuPilotClient, exclude_options):
        """Test excluding specific fields from response."""
        result = client._get_units(exclude=exclude_options, limit=5)
        assert_get_units_success(result)
        
        # Verify excluded fields are not present in the response
        for unit in result["data"]:
            for excluded_field in exclude_options:
                assert excluded_field not in unit, \
                    f"Excluded field '{excluded_field}' should not be present"
    
    def test_exclude_all(self, client: TofuPilotClient):
        """Test excluding specific fields from response."""
        result = client._get_units(exclude=["all"], limit=5)
        assert_get_units_success(result)
        
        # Verify excluded fields are not present in the response
        for unit in result["data"]:
            for excluded_field in self.all_exclude_options:
                assert excluded_field not in unit, \
                    f"Excluded field '{excluded_field}' should not be present"

    def test_complex_filter_combination(self, client: TofuPilotClient):
        """Test combining multiple filters."""
        # Get some units first to find one with part number
        all_units = client._get_units(limit=10)
        assert_get_units_success(all_units)
        
        # Find a unit with revision.component.partNumber
        test_part_number = None
        for unit in all_units["data"]:
            if (unit.get("revision") and 
                unit["revision"].get("component") and 
                unit["revision"]["component"].get("partNumber")):
                test_part_number = unit["revision"]["component"]["partNumber"]
                break
        
        # Skip test if no units with part numbers found
        if not test_part_number:
            pytest.skip("No units with part numbers available for testing")
        
        result = client._get_units(
            partNumbers=[test_part_number],
            limit=10,
            sort="-createdAt",
            exclude=["runs"]
        )
        assert_get_units_success(result)
        
        # Verify filters are applied
        for unit in result["data"]:
            # Check part number filter
            assert (unit.get("revision") and 
                   unit["revision"].get("component") and 
                   unit["revision"]["component"].get("partNumber") == test_part_number)
            
            # Check excluded fields
            assert "runs" not in unit or unit["runs"] is None

    def test_empty_filters(self, client: TofuPilotClient):
        """Test with empty filter lists."""
        result = client._get_units(
            serialNumbers=[],
            partNumbers=[],
            ids=[]
        )
        assert_get_units_success(result)
        # Empty filters should return all units (up to default limit)

    def test_by_ids(self, client: TofuPilotClient):
        """Test filtering units by IDs."""
        # First get some units to get actual IDs
        all_units = client._get_units(limit=3)
        assert_get_units_success(all_units)
        
        # Skip test if no units exist
        if not all_units["data"]:
            pytest.skip("No units available for testing")
            
        # Use the first unit's ID for filtering
        test_id = all_units["data"][0]["id"]
        result = client._get_units(ids=[test_id])
        assert_get_units_success(result)
        
        # Should return exactly one unit with the specified ID
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == test_id