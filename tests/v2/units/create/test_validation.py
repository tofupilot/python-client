"""Test unit creation validation rules."""

import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND, ErrorCONFLICT


class TestCreateUnitValidation:

    def test_create_unit_revision_not_found(self, client: TofuPilot) -> None:
        """Test creating a unit with non-existent revision."""
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        fake_part_number = f"FAKE-PART-{timestamp}"
        fake_revision_number = f"FAKE-REV-{timestamp}"
        serial_number = f"UNIT-{uuid.uuid4().hex[:8]}"
        
        with pytest.raises(ErrorNOTFOUND) as exc_info:
            client.units.create(
                serial_number=serial_number,
                part_number=fake_part_number,
                revision_number=fake_revision_number,
            )
        
        error_message = str(exc_info.value).lower()
        assert "revision" in error_message


    def test_create_unit_duplicate_serial_number(self, client: TofuPilot) -> None:
        """Test creating a unit with duplicate serial number."""
        # Create test data: part and revision
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"UNIT-DUP-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Duplicate Unit {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        serial_number = f"UNIT-DUP-TEST-{uuid.uuid4().hex[:8]}"
        
        # Create first unit
        response1 = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number,
        )
        assert response1.id is not None
        
        # Try to create duplicate
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.units.create(
                serial_number=serial_number,
                part_number=part_number,
                revision_number=revision_number,
            )
        
        error_message = str(exc_info.value).lower()
        assert "already exists" in error_message or "serial number" in error_message

    def test_create_unit_empty_serial_number(self, client: TofuPilot) -> None:
        """Test creating a unit with empty serial number."""
        # Create test data: part and revision
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"UNIT-EMPTY-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Empty Serial {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        
        with pytest.raises(Exception) as exc_info:
            client.units.create(
                serial_number="",
                part_number=part_number,
                revision_number=revision_number,
            )
        
        error_message = str(exc_info.value).lower()
        assert "validation" in error_message or "serial_number" in error_message or "at least 1 character" in error_message

    def test_create_unit_whitespace_only_serial_number(self, client: TofuPilot) -> None:
        """Test creating a unit with whitespace-only serial number."""
        # Create test data: part and revision
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"UNIT-WS-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Whitespace Serial {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        
        with pytest.raises(Exception) as exc_info:
            client.units.create(
                serial_number="   ",
                part_number=part_number,
                revision_number=revision_number,
            )
        
        error_message = str(exc_info.value).lower()
        assert "validation" in error_message or "serial_number" in error_message or "at least 1 character" in error_message