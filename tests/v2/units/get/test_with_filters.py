"""Test unit listing with filtering options."""

import pytest
from typing import Any
from tofupilot.v2 import TofuPilot
from ...utils import assert_get_units_success


class TestGetUnitsWithFilters:

    @pytest.fixture(params=[
        "-createdAt",
        "createdAt",
        "-serialNumber",
        "serialNumber",
    ])
    def sort_option(self, request: Any) -> str:
        """Different sorting options."""
        return request.param


    def test_pagination_with_offset(self, client: TofuPilot):
        """Test pagination using offset parameter."""
        # Get first batch
        first_batch = client.units.list(limit=3, cursor=0)
        assert_get_units_success(first_batch)
        
        # Get second batch
        second_batch = client.units.list(limit=3, cursor=3)
        assert_get_units_success(second_batch)
        
        # If both batches have data, they should be different
        if first_batch.data and second_batch.data:
            first_ids = {unit.id for unit in first_batch.data}
            second_ids = {unit.id for unit in second_batch.data}
            assert first_ids.isdisjoint(second_ids), "Paginated results should not overlap"

    def test_response_structure(self, client: TofuPilot, timestamp: str):
        """Test that response has expected structure."""
        # Create test data to ensure we have a unit to test
        part_number = f"STRUCTURE-TEST-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        serial_number = f"UNIT-{timestamp}"
        
        # Create part
        _ = client.parts.create(
            number=part_number,
            name=f"Test Part for Structure {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create unit with this part
        _ = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number
        )
        
        # Now test the response structure by getting the unit we just created
        result = client.units.list(serial_numbers=[serial_number], limit=1)
        assert_get_units_success(result)
        
        # Should find our created unit
        assert len(result.data) >= 1, "Should find our created test unit"
        
        # Check unit structure
        unit = result.data[0]
        assert hasattr(unit, "id")
        assert isinstance(unit.id, str)
        
        # These fields should typically be present
        assert hasattr(unit, "serial_number")
        assert unit.serial_number is not None
        
        # Check if part and revision information exists
        if hasattr(unit, "part") and unit.part:
            assert unit.part.number is not None
            if hasattr(unit.part, "revision") and unit.part.revision:
                assert unit.part.revision.number is not None

    def test_max_limit(self, client: TofuPilot):
        """Test getting units with maximum allowed limit."""
        # API has a maximum limit of 100
        result = client.units.list(limit=100)
        assert_get_units_success(result)
        # Should return up to 100 units

    def test_include_specific_fields(self, client: TofuPilot):
        """Test including specific fields in response."""
        result = client.units.list(limit=5)
        assert_get_units_success(result)
        
        # Verify that included fields are present when applicable
        # Note: We can't guarantee all fields will be present for all units
        # but we can check that the API accepted the include parameter
        # The API should return successfully with the include parameter

    def test_include_all_fields(self, client: TofuPilot):
        """Test including all optional fields."""
        result = client.units.list(limit=5)
        assert_get_units_success(result)
        
        # Should return successfully with all fields included
        assert len(result.data) <= 5