"""Test minimal unit creation with just required parameters."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_unit_success, get_unit_by_id


class TestCreateUnitMinimal:

    def test_minimal_unit_creation(self, client: TofuPilot, timestamp: str) -> None:
        """Test minimal unit creation with all required parameters."""
        # Create test data: part and revision
        part_number = f"UNIT-MINIMAL-PART-{timestamp}"
        revision_number = f"REV-MINIMAL-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Minimal Unit {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        serial_number = f"AutomatedTest-V2-Unit-{timestamp}"
        
        # Create unit using SDK
        result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number,
        )
        
        # Verify successful response
        assert_create_unit_success(result)
        
        # Verify the unit was created with correct data
        unit = get_unit_by_id(client, result.id)
        assert unit is not None
        assert unit.serial_number == serial_number
        assert unit.part.number == part_number
        assert unit.part.revision.number == revision_number
        assert unit.batch is None  # No batch specified


    def test_unit_creation_with_max_length_serial_number(self, client: TofuPilot, timestamp: str) -> None:
        """Test unit creation with maximum allowed length for serial number (60 chars)."""
        # Create test data: part and revision
        part_number = f"UNIT-MAXLEN-PART-{timestamp}"
        revision_number = f"REV-MAXLEN-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Max Length Unit {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        
        # Create a 60-character serial number
        prefix = f"MAX-LEN-{timestamp}-"
        padding_length = 60 - len(prefix)
        serial_number = prefix + "X" * padding_length
        
        assert len(serial_number) == 60, f"Expected 60 chars, got {len(serial_number)}"
        
        # Create unit
        result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number,
        )
        
        # Verify successful response
        assert_create_unit_success(result)
        
        # Verify the unit was created
        unit = get_unit_by_id(client, result.id)
        assert unit is not None
        assert unit.serial_number == serial_number
        assert len(unit.serial_number) == 60