"""Test unit, part, and revision lifecycle in run creation."""

import uuid
from datetime import datetime, timedelta, timezone
from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success


class TestUnitPartRevisionLifecycle:

    def test_unit_part_revision_creation_and_reuse(self, client: TofuPilot, procedure_id: str) -> None:
        """Test complete lifecycle of unit, part, and revision creation and reuse."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        SERIAL_NUMBER = f"TestUnit-{unique_id}"
        PART_NUMBER = f"TestPart-{unique_id}"
        REVISION_NUMBER = f"Rev-{unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW

        # Test 1: Create first run with new unit, part, and revision
        result1 = client.runs.create(
            serial_number=SERIAL_NUMBER,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            started_at=START_TIME,
            ended_at=END_TIME,
        )
        
        assert_create_run_success(result1)
        
        # Get the created run details
        run1 = client.runs.get(id=result1.id)
        
        # Verify unit was created properly
        assert run1.unit is not None
        assert run1.unit.serial_number == SERIAL_NUMBER
        assert run1.unit.part is not None
        assert run1.unit.part.number == PART_NUMBER
        assert run1.unit.part.revision is not None
        assert run1.unit.part.revision.number == REVISION_NUMBER
        
        # Store IDs for comparison
        unit_id_1 = run1.unit.id
        part_id_1 = run1.unit.part.id
        revision_id_1 = run1.unit.part.revision.id
        
        # Test 2: Create second run with same serial number (should reuse unit)
        START_TIME_2 = NOW - timedelta(minutes=3)
        END_TIME_2 = NOW - timedelta(minutes=1)
        
        result2 = client.runs.create(
            serial_number=SERIAL_NUMBER,  # Same serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            started_at=START_TIME_2,
            ended_at=END_TIME_2,
        )
        
        assert_create_run_success(result2)
        
        # Get the second run details
        run2 = client.runs.get(id=result2.id)
        
        # Verify same unit was reused
        assert run2.unit is not None
        unit2 = run2.unit
        assert unit2.id == unit_id_1  # Same unit ID
        assert unit2.serial_number == SERIAL_NUMBER
        assert unit2.part is not None
        part2 = unit2.part
        assert part2.id == part_id_1  # Same part ID
        assert part2.number == PART_NUMBER
        assert part2.revision is not None
        revision2 = part2.revision
        assert revision2.id == revision_id_1  # Same revision ID
        assert revision2.number == REVISION_NUMBER
        
        # Test 3: Create third run with different serial but same part (should create new unit, reuse part)
        SERIAL_NUMBER_3 = f"TestUnit-{unique_id}-Different"
        START_TIME_3 = NOW - timedelta(minutes=2)
        END_TIME_3 = NOW - timedelta(seconds=30)
        
        result3 = client.runs.create(
            serial_number=SERIAL_NUMBER_3,  # Different serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,  # Same part number
            revision_number=REVISION_NUMBER,  # Same revision
            started_at=START_TIME_3,
            ended_at=END_TIME_3,
        )
        
        assert_create_run_success(result3)
        
        # Get the third run details
        run3 = client.runs.get(id=result3.id)
        
        # Verify new unit was created but same part was reused
        assert run3.unit is not None
        unit3 = run3.unit
        assert unit3.id != unit_id_1  # Different unit ID
        assert unit3.serial_number == SERIAL_NUMBER_3
        assert unit3.part is not None
        part3 = unit3.part
        assert part3.id == part_id_1  # Same part ID (reused)
        assert part3.number == PART_NUMBER
        assert part3.revision is not None
        revision3 = part3.revision
        assert revision3.id == revision_id_1  # Same revision ID (reused)
        assert revision3.number == REVISION_NUMBER
        
        # Test 4: Create fourth run with same part but different revision (should create new revision)
        SERIAL_NUMBER_4 = f"TestUnit-{unique_id}-Rev2"
        REVISION_NUMBER_4 = f"Rev-{unique_id}-B"
        START_TIME_4 = NOW - timedelta(minutes=1)
        END_TIME_4 = NOW
        
        result4 = client.runs.create(
            serial_number=SERIAL_NUMBER_4,  # Different serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,  # Same part number
            revision_number=REVISION_NUMBER_4,  # Different revision
            started_at=START_TIME_4,
            ended_at=END_TIME_4,
        )
        
        assert_create_run_success(result4)
        
        # Get the fourth run details
        run4 = client.runs.get(id=result4.id)
        
        # Verify new unit and revision were created but same part was reused
        assert run4.unit is not None
        unit4 = run4.unit
        assert unit4.id != unit_id_1  # Different unit ID
        assert unit4.id != unit3.id  # Different from run3 unit ID
        assert unit4.serial_number == SERIAL_NUMBER_4
        assert unit4.part is not None
        part4 = unit4.part
        assert part4.id == part_id_1  # Same part ID (reused)
        assert part4.number == PART_NUMBER
        assert part4.revision is not None
        revision4 = part4.revision
        assert revision4.id != revision_id_1  # Different revision ID
        assert revision4.number == REVISION_NUMBER_4
        
        # Store new revision ID for final test
        revision_id_4 = revision4.id
        
        # Test 5: Create fifth run reusing the second revision
        SERIAL_NUMBER_5 = f"TestUnit-{unique_id}-Rev2-Reuse"
        START_TIME_5 = NOW
        END_TIME_5 = NOW + timedelta(minutes=1)
        
        result5 = client.runs.create(
            serial_number=SERIAL_NUMBER_5,  # Different serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,  # Same part number
            revision_number=REVISION_NUMBER_4,  # Same revision as run4
            started_at=START_TIME_5,
            ended_at=END_TIME_5,
        )
        
        assert_create_run_success(result5)
        
        # Get the fifth run details
        run5 = client.runs.get(id=result5.id)
        
        # Verify new unit was created but same part and revision were reused
        assert run5.unit is not None
        unit5 = run5.unit
        assert unit5.id != unit_id_1  # Different unit ID
        assert unit5.id != unit3.id  # Different from run3 unit ID
        assert unit5.id != unit4.id  # Different from run4 unit ID
        assert unit5.serial_number == SERIAL_NUMBER_5
        assert unit5.part is not None
        part5 = unit5.part
        assert part5.id == part_id_1  # Same part ID (reused)
        assert part5.number == PART_NUMBER
        assert part5.revision is not None
        revision5 = part5.revision
        assert revision5.id == revision_id_4  # Same revision ID as run4 (reused)
        assert revision5.number == REVISION_NUMBER_4
        
        # Verify all runs have correct basic properties
        for run, expected_serial in [
            (run1, SERIAL_NUMBER),
            (run2, SERIAL_NUMBER), 
            (run3, SERIAL_NUMBER_3),
            (run4, SERIAL_NUMBER_4),
            (run5, SERIAL_NUMBER_5)
        ]:
            assert run.outcome == OUTCOME
            assert run.procedure is not None
            assert run.procedure.id == procedure_id
            assert run.unit is not None
            assert run.unit.serial_number == expected_serial
            assert run.unit.part is not None
            assert run.unit.part.number == PART_NUMBER