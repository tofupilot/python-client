"""Test case-insensitive conflict detection for unit updates."""
import pytest
import uuid
from datetime import datetime, timezone, timedelta
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorCONFLICT, APIError


@pytest.mark.parametrize("client", ["user"], indirect=True)
class TestUnitUpdateCaseInsensitiveConflicts:
    """Test that unit updates detect case-insensitive conflicts."""

    @pytest.fixture
    def procedure_id(self, client: TofuPilot, auth_type: str) -> str:
        """Create a procedure for testing."""
        if auth_type == "station":
            # Stations cannot create procedures, skip these tests
            pytest.skip("Stations cannot create procedures")
        
        procedure = client.procedures.create(
            name=f"Test Procedure {uuid.uuid4()}"
        )
        return procedure.id

    def test_unit_serial_number_update_case_insensitive_conflict(self, client: TofuPilot, procedure_id: str):
        """Test that updating unit serial number with different case throws conflict error."""
        now = datetime.now(timezone.utc)
        
        # Create two units with different serial numbers
        serial1 = f"UNIT-{uuid.uuid4()}"
        serial2 = f"UNIT-{uuid.uuid4()}"
        
        # Create runs to create the units
        run1 = client.runs.create(
            serial_number=serial1.upper(),
            part_number=f"part-{uuid.uuid4()}",
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=10),
            ended_at=now - timedelta(minutes=9)
        )
        
        run2 = client.runs.create(
            serial_number=serial2.upper(),
            part_number=f"part-{uuid.uuid4()}",
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=8),
            ended_at=now - timedelta(minutes=7)
        )
        
        # Get the unit serial numbers
        run1_details = client.runs.get(id=run1.id)
        run2_details = client.runs.get(id=run2.id)
        unit1_serial = run1_details.unit.serial_number
        unit2_serial = run2_details.unit.serial_number
        
        # Try to update unit2's serial number to match unit1's (but with different case)
        # This should fail with a conflict
        with pytest.raises(ErrorCONFLICT) as e:
            client.units.update(
                serial_number=unit2_serial,
                new_serial_number=serial1.lower()  # Same as unit1 but lowercase
            )
            # Should get 409 CONFLICT for duplicate serial numbers
            error_msg = str(e).lower()
            assert any(phrase in error_msg for phrase in ["already in use", "already exists", "serial number is already"])

    def test_unit_serial_number_update_whitespace_conflict(self, client: TofuPilot, procedure_id: str):
        """Test that whitespace is normalized in serial number conflict detection."""
        now = datetime.now(timezone.utc)
        
        # Create two units
        serial1 = f"UNIT-{uuid.uuid4()}"
        serial2 = f"UNIT-{uuid.uuid4()}"
        
        # Create runs
        run1 = client.runs.create(
            serial_number=f"  {serial1}  ",  # With spaces
            part_number=f"part-{uuid.uuid4()}",
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=10),
            ended_at=now - timedelta(minutes=9)
        )
        
        run2 = client.runs.create(
            serial_number=serial2,
            part_number=f"part-{uuid.uuid4()}",
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=8),
            ended_at=now - timedelta(minutes=7)
        )
        
        # Get unit serial numbers
        run1_details = client.runs.get(id=run1.id)
        run2_details = client.runs.get(id=run2.id)
        unit2_serial = run2_details.unit.serial_number
        
        # Try to update unit2 to have unit1's serial (without spaces)
        try:
            client.units.update(
                serial_number=unit2_serial,
                new_serial_number=serial1  # Without spaces
            )
            pytest.fail("Expected error when updating unit serial number to conflict")
        except ErrorCONFLICT as e:
            error_msg = str(e).lower()
            assert any(phrase in error_msg for phrase in ["already in use", "already exists", "serial number is already"])

    def test_unit_serial_number_update_no_conflict(self, client: TofuPilot, procedure_id: str):
        """Test that updating unit serial number to a unique value works."""
        now = datetime.now(timezone.utc)
        
        # Create a unit
        serial1 = f"UNIT-{uuid.uuid4()}"
        new_serial = f"UNIT-NEW-{uuid.uuid4()}"
        
        run1 = client.runs.create(
            serial_number=serial1,
            part_number=f"part-{uuid.uuid4()}",
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=10),
            ended_at=now - timedelta(minutes=9)
        )
        
        # Get unit serial number
        run1_details = client.runs.get(id=run1.id)
        unit1_serial = run1_details.unit.serial_number
        
        # Update to a new unique serial number - should succeed
        updated_unit = client.units.update(
            serial_number=unit1_serial,
            new_serial_number=new_serial
        )
        
        # Verify the update succeeded by fetching the unit
        updated_unit_details = client.units.get(serial_number=new_serial)
        assert updated_unit_details.serial_number == new_serial