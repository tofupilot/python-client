"""Test unit update operations."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_unit_success, assert_update_unit_success, get_unit_by_id
from ...utils import assert_station_access_limited


class TestUnitsUpdate:
    
    def test_update_unit_basic(self, client: TofuPilot, auth_type: str):
        """Test updating a unit with basic fields."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        # Create test parts and revisions
        part1_number = f"UPDATE-BASIC-PART1-{timestamp}"
        part2_number = f"UPDATE-BASIC-PART2-{timestamp}"
        revision1_number = f"REV1-{timestamp}"
        revision2_number = f"REV2-{timestamp}"
        
        # Create first part and revision
        client.parts.create(
            number=part1_number,
            name=f"Test Part 1 for Update {timestamp}"
        )
        revision1_result = client.parts.revisions.create(
            part_number=part1_number,
            number=revision1_number
        )
        
        # Create second part and revision
        client.parts.create(
            number=part2_number,
            name=f"Test Part 2 for Update {timestamp}"
        )
        client.parts.revisions.create(
            part_number=part2_number,
            number=revision2_number
        )
        
        # Create unit
        serial_number = f"AutomatedTest-V2-UpdateBasic-{timestamp}"
        create_result = client.units.create(
            serial_number=serial_number,
            part_number=part1_number,
            revision_number=revision1_number,
        )
        assert_create_unit_success(create_result)
        
        if auth_type == "station":
            # Stations have limited access to update units
            with assert_station_access_limited("update unit with basic fields"):
                result = client.units.update(
                    serial_number=serial_number,
                    new_serial_number=f"UpdatedSerial-{timestamp}",
                    part_number=part2_number,
                    revision_number=revision2_number,
                    batch_number="Batch789"
                )
            return
        
        # Update with new fields
        new_serial = f"UpdatedSerial-{timestamp}"
        result = client.units.update(
            serial_number=serial_number,
            new_serial_number=new_serial,
            part_number=part2_number,
            revision_number=revision2_number,
            batch_number="Batch789"
        )
        
        assert_update_unit_success(result)
        assert result.id == create_result.id
        
        # Verify the update
        updated_unit = get_unit_by_id(client, create_result.id)
        assert updated_unit is not None
        assert updated_unit.serial_number == new_serial
        assert updated_unit.part.number == part2_number
        assert updated_unit.part.revision.number == revision2_number
    
    def test_update_unit_minimal(self, client: TofuPilot, auth_type: str):
        """Test updating a unit with minimal parameters."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        # Create test part and revision
        part_number = f"UPDATE-MINIMAL-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        client.parts.create(
            number=part_number,
            name=f"Test Part for Update {timestamp}"
        )
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create unit
        serial_number = f"AutomatedTest-V2-UpdateMinimal-{timestamp}"
        create_result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number,
        )
        assert_create_unit_success(create_result)
        
        if auth_type == "station":
            # Stations have limited access to update units
            with assert_station_access_limited("update unit with minimal parameters"):
                result = client.units.update(
                    serial_number=serial_number,
                    new_serial_number=f"UpdatedSerial-{timestamp}"
                )
            return
        
        # Update with minimal parameters
        new_serial = f"UpdatedSerial-{timestamp}"
        result = client.units.update(
            serial_number=serial_number,
            new_serial_number=new_serial
        )
        
        assert_update_unit_success(result)
        assert result.id == create_result.id
        
        # Verify the update
        updated_unit = get_unit_by_id(client, create_result.id)
        assert updated_unit is not None
        assert updated_unit.serial_number == new_serial