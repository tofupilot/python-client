"""Test unit listing with part and revision filtering using AND logic."""

import pytest
from datetime import datetime, timezone
from typing import Any
from tofupilot.v2 import TofuPilot
from ...utils import assert_get_units_success


class TestPartRevisionFiltering:
    """Test filtering units by part numbers and revision numbers with AND logic."""

    @pytest.fixture
    def test_data(self, client: TofuPilot) -> dict[str, Any]:
        """Create test data with specific parts and revisions."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        # Create two parts with different revisions
        part1_number = f"FILTER-PART1-{timestamp}"
        part2_number = f"FILTER-PART2-{timestamp}"
        
        # Create parts
        part1 = client.parts.create(
            number=part1_number,
            name=f"Filter Test Part 1 {timestamp}"
        )
        
        part2 = client.parts.create(
            number=part2_number,
            name=f"Filter Test Part 2 {timestamp}"
        )
        
        # Create revisions for each part
        rev1_1 = client.parts.revisions.create(
            part_number=part1_number,
            number=f"REV1.1-{timestamp}"
        )
        
        rev1_2 = client.parts.revisions.create(
            part_number=part1_number,
            number=f"REV1.2-{timestamp}"
        )
        
        rev2_1 = client.parts.revisions.create(
            part_number=part2_number,
            number=f"REV2.1-{timestamp}"
        )
        
        # Create units for different combinations
        unit_serials = []
        
        # Unit with Part1, Rev1.1
        serial1 = f"UNIT-P1R1-{timestamp}"
        client.units.create(
            serial_number=serial1,
            part_number=part1_number,
            revision_number=f"REV1.1-{timestamp}"
        )
        unit_serials.append(serial1)
        
        # Unit with Part1, Rev1.2
        serial2 = f"UNIT-P1R2-{timestamp}"
        client.units.create(
            serial_number=serial2,
            part_number=part1_number,
            revision_number=f"REV1.2-{timestamp}"
        )
        unit_serials.append(serial2)
        
        # Unit with Part2, Rev2.1
        serial3 = f"UNIT-P2R1-{timestamp}"
        client.units.create(
            serial_number=serial3,
            part_number=part2_number,
            revision_number=f"REV2.1-{timestamp}"
        )
        unit_serials.append(serial3)
        
        return {
            "part1_number": part1_number,
            "part2_number": part2_number,
            "rev1_1_number": f"REV1.1-{timestamp}",
            "rev1_2_number": f"REV1.2-{timestamp}",
            "rev2_1_number": f"REV2.1-{timestamp}",
            "unit_serials": unit_serials
        }

    def test_filter_by_part_only(self, client: TofuPilot, test_data: dict[str, Any]):
        """Test filtering by part number only returns all units of that part."""
        # Filter by part1 only
        result = client.units.list(
            part_numbers=[test_data["part1_number"]],
            serial_numbers=test_data["unit_serials"]  # Limit to our test units
        )
        assert_get_units_success(result)
        
        # Should find 2 units (both revisions of part1)
        assert len(result.data) == 2
        serials = {unit.serial_number for unit in result.data}
        assert all("P1R" in serial for serial in serials)

    def test_filter_by_revision_only(self, client: TofuPilot, test_data: dict[str, Any]):
        """Test filtering by revision number only returns units with that revision."""
        # Filter by rev1.1 only
        result = client.units.list(
            revision_numbers=[test_data["rev1_1_number"]],
            serial_numbers=test_data["unit_serials"]  # Limit to our test units
        )
        assert_get_units_success(result)
        
        # Should find 1 unit with rev1.1
        assert len(result.data) == 1
        assert "P1R1" in result.data[0].serial_number

    def test_filter_by_part_and_revision_and_logic(self, client: TofuPilot, test_data: dict[str, Any]):
        """Test filtering by both part AND revision uses AND logic."""
        # Filter by part1 AND rev1.2
        result = client.units.list(
            part_numbers=[test_data["part1_number"]],
            revision_numbers=[test_data["rev1_2_number"]],
            serial_numbers=test_data["unit_serials"]  # Limit to our test units
        )
        assert_get_units_success(result)
        
        # Should find only 1 unit that matches BOTH part1 AND rev1.2
        assert len(result.data) == 1
        assert "P1R2" in result.data[0].serial_number

    def test_filter_mismatched_part_and_revision(self, client: TofuPilot, test_data: dict[str, Any]):
        """Test filtering with part and revision that don't match returns no results."""
        # Filter by part1 AND rev2.1 (rev2.1 belongs to part2, not part1)
        result = client.units.list(
            part_numbers=[test_data["part1_number"]],
            revision_numbers=[test_data["rev2_1_number"]],
            serial_numbers=test_data["unit_serials"]  # Limit to our test units
        )
        assert_get_units_success(result)
        
        # Should find no units since no unit has part1 AND rev2.1
        assert len(result.data) == 0

    def test_filter_multiple_parts_and_revisions(self, client: TofuPilot, test_data: dict[str, Any]):
        """Test filtering with multiple parts and revisions."""
        # Filter by (part1 OR part2) AND (rev1.1 OR rev2.1)
        result = client.units.list(
            part_numbers=[test_data["part1_number"], test_data["part2_number"]],
            revision_numbers=[test_data["rev1_1_number"], test_data["rev2_1_number"]],
            serial_numbers=test_data["unit_serials"]  # Limit to our test units
        )
        assert_get_units_success(result)
        
        # Should find 2 units:
        # - Unit with part1 AND rev1.1 ✓
        # - Unit with part2 AND rev2.1 ✓
        # - Unit with part1 AND rev1.2 ✗ (rev1.2 not in filter)
        assert len(result.data) == 2
        serials = {unit.serial_number for unit in result.data}
        assert any("P1R1" in s for s in serials)  # Part1 with Rev1.1
        assert any("P2R1" in s for s in serials)  # Part2 with Rev2.1

    def test_empty_filters_return_all(self, client: TofuPilot, test_data: dict[str, Any]):
        """Test that empty part/revision filters return all units."""
        # No part or revision filters
        result = client.units.list(
            serial_numbers=test_data["unit_serials"]  # Limit to our test units
        )
        assert_get_units_success(result)
        
        # Should find all 3 test units
        assert len(result.data) == 3