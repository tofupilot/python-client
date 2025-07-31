"""Test procedure version lifecycle in run creation."""

import uuid
from datetime import datetime, timedelta, timezone
from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success


class TestProcedureVersionLifecycle:

    def test_procedure_version_creation_and_reuse(self, client: TofuPilot, procedure_id: str) -> None:
        """Test basic procedure assignment in run creation."""
        
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        SERIAL_NUMBER_1 = f"TestUnit-ProcVer1-{unique_id}"
        SERIAL_NUMBER_2 = f"TestUnit-ProcVer2-{unique_id}"
        PART_NUMBER = f"TestPart-ProcVer-{unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW

        # Test 1: Create first run with basic procedure assignment
        result1 = client.runs.create(
            serial_number=SERIAL_NUMBER_1,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            started_at=START_TIME,
            ended_at=END_TIME,
        )
        
        assert_create_run_success(result1)
        
        # Get the created run details
        run1 = client.runs.get(id=result1.id)
        
        # Verify procedure was assigned properly
        assert run1.procedure is not None
        procedure1 = run1.procedure
        assert procedure1.id == procedure_id
        
        # Test 2: Create second run with same procedure (should reuse)
        START_TIME_2 = NOW - timedelta(minutes=3)
        END_TIME_2 = NOW - timedelta(minutes=1)
        
        result2 = client.runs.create(
            serial_number=SERIAL_NUMBER_2,  # Different serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            started_at=START_TIME_2,
            ended_at=END_TIME_2,
        )
        
        assert_create_run_success(result2)
        
        # Get the second run details
        run2 = client.runs.get(id=result2.id)
        
        # Verify same procedure was reused
        assert run2.procedure is not None
        procedure2 = run2.procedure
        assert procedure2.id == procedure_id
        
        # Verify both runs have correct basic properties
        for run, expected_serial in [(run1, SERIAL_NUMBER_1), (run2, SERIAL_NUMBER_2)]:
            assert run.outcome == OUTCOME
            assert run.procedure is not None
            assert run.procedure.id == procedure_id
            assert run.unit is not None
            assert run.unit.serial_number == expected_serial
            assert run.unit.part is not None
            assert run.unit.part.number == PART_NUMBER