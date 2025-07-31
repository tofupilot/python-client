"""Test sub_units lifecycle in run creation."""

import uuid
from datetime import datetime, timedelta, timezone
from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success


class TestSubUnitsLifecycle:

    def test_sub_units_creation_and_linking(self, client: TofuPilot, procedure_id: str) -> None:
        """Test complete lifecycle of sub-units creation and linking."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        
        # Main unit and sub-units
        MAIN_SERIAL = f"MainUnit-{unique_id}"
        SUB_SERIAL_1 = f"SubUnit1-{unique_id}"
        SUB_SERIAL_2 = f"SubUnit2-{unique_id}"
        
        # Parts
        MAIN_PART = f"MainPart-{unique_id}"
        SUB_PART_1 = f"SubPart1-{unique_id}"
        SUB_PART_2 = f"SubPart2-{unique_id}"
        
        # Revisions
        MAIN_REVISION = f"MainRev-{unique_id}"
        SUB_REVISION_1 = f"SubRev1-{unique_id}"
        SUB_REVISION_2 = f"SubRev2-{unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        
        # Test 1: Create first sub-unit
        START_TIME_1 = NOW - timedelta(minutes=10)
        END_TIME_1 = NOW - timedelta(minutes=8)
        
        result1 = client.runs.create(
            serial_number=SUB_SERIAL_1,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=SUB_PART_1,
            revision_number=SUB_REVISION_1,
            started_at=START_TIME_1,
            ended_at=END_TIME_1,
        )
        
        assert_create_run_success(result1)
        
        # Get the created sub-unit run
        sub_run1 = client.runs.get(id=result1.id)
        
        # Verify sub-unit was created properly
        assert sub_run1.unit is not None
        assert sub_run1.unit.serial_number == SUB_SERIAL_1
        assert sub_run1.unit.part is not None
        assert sub_run1.unit.part.number == SUB_PART_1
        
        # Test 2: Create second sub-unit
        START_TIME_2 = NOW - timedelta(minutes=8)
        END_TIME_2 = NOW - timedelta(minutes=6)
        
        result2 = client.runs.create(
            serial_number=SUB_SERIAL_2,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=SUB_PART_2,
            revision_number=SUB_REVISION_2,
            started_at=START_TIME_2,
            ended_at=END_TIME_2,
        )
        
        assert_create_run_success(result2)
        
        # Get the created sub-unit run
        sub_run2 = client.runs.get(id=result2.id)
        
        # Verify second sub-unit was created properly
        assert sub_run2.unit is not None
        assert sub_run2.unit.serial_number == SUB_SERIAL_2
        assert sub_run2.unit.part is not None
        assert sub_run2.unit.part.number == SUB_PART_2
        
        # Test 3: Create main unit with sub-units
        START_TIME_3 = NOW - timedelta(minutes=5)
        END_TIME_3 = NOW
        
        result3 = client.runs.create(
            serial_number=MAIN_SERIAL,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=MAIN_PART,
            revision_number=MAIN_REVISION,
            sub_units=[SUB_SERIAL_1, SUB_SERIAL_2],
            started_at=START_TIME_3,
            ended_at=END_TIME_3,
        )
        
        assert_create_run_success(result3)
        
        # Get the created main unit run
        main_run = client.runs.get(id=result3.id)
        
        # Verify main unit was created properly
        assert main_run.unit is not None
        assert main_run.unit.serial_number == MAIN_SERIAL
        assert main_run.unit.part is not None
        assert main_run.unit.part.number == MAIN_PART
        
        # Verify all runs have correct basic properties
        all_runs = [
            (sub_run1, SUB_SERIAL_1, SUB_PART_1),
            (sub_run2, SUB_SERIAL_2, SUB_PART_2),
            (main_run, MAIN_SERIAL, MAIN_PART),
        ]
        
        for run, expected_serial, expected_part in all_runs:
            assert run.outcome == OUTCOME
            assert run.procedure is not None
            assert run.procedure.id == procedure_id
            assert run.unit is not None
            assert run.unit.serial_number == expected_serial
            assert run.unit.part is not None
            assert run.unit.part.number == expected_part

    def test_run_without_sub_units(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that runs without sub_units work normally."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        SERIAL_NUMBER = f"TestUnit-NoSub-{unique_id}"
        PART_NUMBER = f"TestPart-NoSub-{unique_id}"
        REVISION_NUMBER = f"Rev-NoSub-{unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW

        # Create run without sub_units
        result = client.runs.create(
            serial_number=SERIAL_NUMBER,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            started_at=START_TIME,
            ended_at=END_TIME,
        )
        
        assert_create_run_success(result)
        
        # Get the created run details
        run = client.runs.get(id=result.id)
        
        # Verify run was created without sub-units
        assert run.outcome == OUTCOME
        assert run.procedure is not None
        assert run.procedure.id == procedure_id
        assert run.unit is not None
        assert run.unit.serial_number == SERIAL_NUMBER
        assert run.unit.part is not None
        assert run.unit.part.number == PART_NUMBER

    def test_run_with_empty_sub_units(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that runs with empty sub_units array work properly."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        SERIAL_NUMBER = f"TestUnit-EmptySub-{unique_id}"
        PART_NUMBER = f"TestPart-EmptySub-{unique_id}"
        REVISION_NUMBER = f"Rev-EmptySub-{unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW

        # Create run with empty sub_units array
        result = client.runs.create(
            serial_number=SERIAL_NUMBER,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            sub_units=[],
            started_at=START_TIME,
            ended_at=END_TIME,
        )
        
        assert_create_run_success(result)
        
        # Get the created run details
        run = client.runs.get(id=result.id)
        
        # Verify run was created with empty sub-units
        assert run.outcome == OUTCOME
        assert run.procedure is not None
        assert run.procedure.id == procedure_id
        assert run.unit is not None
        assert run.unit.serial_number == SERIAL_NUMBER
        assert run.unit.part is not None
        assert run.unit.part.number == PART_NUMBER

    def test_run_with_single_sub_unit(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that runs with a single sub-unit work properly."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        
        MAIN_SERIAL = f"MainUnit-Single-{unique_id}"
        SUB_SERIAL = f"SubUnit-Single-{unique_id}"
        
        MAIN_PART = f"MainPart-Single-{unique_id}"
        SUB_PART = f"SubPart-Single-{unique_id}"
        
        MAIN_REVISION = f"MainRev-Single-{unique_id}"
        SUB_REVISION = f"SubRev-Single-{unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        
        # Create sub-unit first
        START_TIME_1 = NOW - timedelta(minutes=8)
        END_TIME_1 = NOW - timedelta(minutes=6)
        
        result1 = client.runs.create(
            serial_number=SUB_SERIAL,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=SUB_PART,
            revision_number=SUB_REVISION,
            started_at=START_TIME_1,
            ended_at=END_TIME_1,
        )
        
        assert_create_run_success(result1)
        
        # Create main unit with single sub-unit
        START_TIME_2 = NOW - timedelta(minutes=5)
        END_TIME_2 = NOW
        
        result2 = client.runs.create(
            serial_number=MAIN_SERIAL,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=MAIN_PART,
            revision_number=MAIN_REVISION,
            sub_units=[SUB_SERIAL],
            started_at=START_TIME_2,
            ended_at=END_TIME_2,
        )
        
        assert_create_run_success(result2)
        
        # Get both runs
        sub_run = client.runs.get(id=result1.id)
        main_run = client.runs.get(id=result2.id)
        
        # Verify both runs were created properly
        assert sub_run.unit is not None
        assert sub_run.unit.serial_number == SUB_SERIAL
        assert sub_run.unit.part is not None
        assert sub_run.unit.part.number == SUB_PART
        
        assert main_run.unit is not None
        assert main_run.unit.serial_number == MAIN_SERIAL
        assert main_run.unit.part is not None
        assert main_run.unit.part.number == MAIN_PART