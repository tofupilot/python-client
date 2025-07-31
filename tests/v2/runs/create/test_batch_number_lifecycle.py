"""Test batch number lifecycle in run creation."""

import pytest
import uuid
from datetime import datetime, timedelta, timezone
from tofupilot.v2 import TofuPilot
from tofupilot.v2.models import RunGetBatch
from ...utils import assert_create_run_success


class TestBatchNumberLifecycle:

    def test_batch_number_creation_and_reuse(self, client: TofuPilot, procedure_id: str) -> None:
        """Test complete lifecycle of batch number creation and reuse."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        SERIAL_NUMBER_1 = f"TestUnit-Batch1-{unique_id}"
        SERIAL_NUMBER_2 = f"TestUnit-Batch2-{unique_id}"
        SERIAL_NUMBER_3 = f"TestUnit-Batch3-{unique_id}"
        SERIAL_NUMBER_4 = f"TestUnit-Batch4-{unique_id}"
        PART_NUMBER = f"TestPart-Batch-{unique_id}"
        REVISION_NUMBER = f"Rev-Batch-{unique_id}"
        BATCH_NUMBER = f"Batch-{unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW

        # Stations can now create runs with batch numbers

        # Test 1: Create first run with new batch number
        result1 = client.runs.create(
            serial_number=SERIAL_NUMBER_1,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            batch_number=BATCH_NUMBER,
            started_at=START_TIME,
            ended_at=END_TIME,
        )
        
        assert_create_run_success(result1)
        
        # Get the created run details
        run1 = client.runs.get(id=result1.id)
        
        # Verify batch was created properly
        assert run1.unit is not None
        unit1 = run1.unit
        assert unit1.serial_number == SERIAL_NUMBER_1
        assert unit1.batch is not None
        
        # Store batch ID for comparison
        from tofupilot.v2.types import UNSET
        batch_id_1 = ""
        if unit1.batch is not UNSET and isinstance(unit1.batch, RunGetBatch):
            assert unit1.batch.number == BATCH_NUMBER
            batch_id_1 = unit1.batch.id
            assert batch_id_1 is not None
        
        # Test 2: Create second run with same batch number (should reuse batch)
        START_TIME_2 = NOW - timedelta(minutes=3)
        END_TIME_2 = NOW - timedelta(minutes=1)
        
        result2 = client.runs.create(
            serial_number=SERIAL_NUMBER_2,  # Different serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            batch_number=BATCH_NUMBER,  # Same batch number
            started_at=START_TIME_2,
            ended_at=END_TIME_2,
        )
        
        assert_create_run_success(result2)
        
        # Get the second run details
        run2 = client.runs.get(id=result2.id)
        
        # Verify same batch was reused
        assert run2.unit is not None
        unit2 = run2.unit
        assert unit2.serial_number == SERIAL_NUMBER_2
        assert unit2.batch is not None
        if unit2.batch is not UNSET and isinstance(unit2.batch, RunGetBatch):
            assert unit2.batch.number == BATCH_NUMBER
            assert unit2.batch.id == batch_id_1
        
        # Test 3: Create third run without batch number (should have no batch)
        START_TIME_3 = NOW - timedelta(minutes=2)
        END_TIME_3 = NOW - timedelta(seconds=30)
        
        result3 = client.runs.create(
            serial_number=SERIAL_NUMBER_3,  # Different serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            # No batch_number provided
            started_at=START_TIME_3,
            ended_at=END_TIME_3,
        )
        
        assert_create_run_success(result3)
        
        # Get the third run details
        run3 = client.runs.get(id=result3.id)
        
        # Verify no batch was assigned
        assert run3.unit is not None
        unit3 = run3.unit
        assert unit3.serial_number == SERIAL_NUMBER_3
        assert unit3.batch is None
        
        # Test 4: Create fourth run with different batch number (should create new batch)
        BATCH_NUMBER_2 = f"Batch-{unique_id}-B"
        START_TIME_4 = NOW - timedelta(minutes=1)
        END_TIME_4 = NOW
        
        result4 = client.runs.create(
            serial_number=SERIAL_NUMBER_4,  # Different serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            batch_number=BATCH_NUMBER_2,  # Different batch number
            started_at=START_TIME_4,
            ended_at=END_TIME_4,
        )
        
        assert_create_run_success(result4)
        
        # Get the fourth run details
        run4 = client.runs.get(id=result4.id)
        
        # Verify new batch was created
        assert run4.unit is not None
        unit4 = run4.unit
        assert unit4.serial_number == SERIAL_NUMBER_4
        assert unit4.batch is not None
        
        # Store new batch ID for final test
        batch_id_2 = ""
        if unit4.batch is not UNSET and isinstance(unit4.batch, RunGetBatch):
            assert unit4.batch.number == BATCH_NUMBER_2
            assert unit4.batch.id != batch_id_1
            batch_id_2 = unit4.batch.id
            assert batch_id_2 is not None
        
        # Test 5: Create fifth run reusing the second batch
        SERIAL_NUMBER_5 = f"TestUnit-Batch5-{unique_id}"
        START_TIME_5 = NOW
        END_TIME_5 = NOW + timedelta(minutes=1)
        
        result5 = client.runs.create(
            serial_number=SERIAL_NUMBER_5,  # Different serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            batch_number=BATCH_NUMBER_2,  # Same batch number as run4
            started_at=START_TIME_5,
            ended_at=END_TIME_5,
        )
        
        assert_create_run_success(result5)
        
        # Get the fifth run details
        run5 = client.runs.get(id=result5.id)
        
        # Verify same batch was reused
        assert run5.unit is not None
        unit5 = run5.unit
        assert unit5.serial_number == SERIAL_NUMBER_5
        assert unit5.batch is not None
        if unit5.batch is not UNSET and isinstance(unit5.batch, RunGetBatch):
            assert unit5.batch.number == BATCH_NUMBER_2
            assert unit5.batch.id == batch_id_2
        
        # Test 6: Create sixth run reusing the first batch
        SERIAL_NUMBER_6 = f"TestUnit-Batch6-{unique_id}"
        START_TIME_6 = NOW + timedelta(minutes=1)
        END_TIME_6 = NOW + timedelta(minutes=2)
        
        result6 = client.runs.create(
            serial_number=SERIAL_NUMBER_6,  # Different serial number
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            batch_number=BATCH_NUMBER,  # Same batch number as run1 and run2
            started_at=START_TIME_6,
            ended_at=END_TIME_6,
        )
        
        assert_create_run_success(result6)
        
        # Get the sixth run details
        run6 = client.runs.get(id=result6.id)
        
        # Verify original batch was reused
        assert run6.unit is not None
        unit6 = run6.unit
        assert unit6.serial_number == SERIAL_NUMBER_6
        assert unit6.batch is not None
        if unit6.batch is not UNSET and isinstance(unit6.batch, RunGetBatch):
            assert unit6.batch.number == BATCH_NUMBER
            assert unit6.batch.id == batch_id_1
        
        # Verify all runs have correct basic properties
        test_runs = [
            (run1, SERIAL_NUMBER_1, BATCH_NUMBER, batch_id_1),
            (run2, SERIAL_NUMBER_2, BATCH_NUMBER, batch_id_1),
            (run4, SERIAL_NUMBER_4, BATCH_NUMBER_2, batch_id_2),
            (run5, SERIAL_NUMBER_5, BATCH_NUMBER_2, batch_id_2),
            (run6, SERIAL_NUMBER_6, BATCH_NUMBER, batch_id_1),
        ]
        
        for run, expected_serial, expected_batch_number, expected_batch_id in test_runs:
            assert run.outcome == OUTCOME
            assert run.procedure is not None
            assert run.procedure.id == procedure_id
            assert run.unit is not None
            assert run.unit.serial_number == expected_serial
            assert run.unit.part is not None
            assert run.unit.part.number == PART_NUMBER
            assert run.unit.batch is not None
            if run.unit.batch is not UNSET and isinstance(run.unit.batch, RunGetBatch):
                assert run.unit.batch.number == expected_batch_number
                assert run.unit.batch.id == expected_batch_id
            
        # Verify run without batch
        assert run3.outcome == OUTCOME
        assert run3.procedure is not None
        assert run3.procedure.id == procedure_id
        assert run3.unit is not None
        assert run3.unit.serial_number == SERIAL_NUMBER_3
        assert run3.unit.part is not None
        assert run3.unit.part.number == PART_NUMBER
        assert run3.unit.batch is None