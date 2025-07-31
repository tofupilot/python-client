"""Test minimal run creation with just required parameters."""

from datetime import datetime, timedelta, timezone
from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success, assert_timestamps_close


class TestCreateRunMinimal:

    def test_minimal_run_creation(self, client: TofuPilot, procedure_id: str) -> None:
        """Test minimal run creation with all required parameters."""
        # Test constants
        SERIAL_NUMBER = "AutomatedTest-V2-Minimal"
        OUTCOME = "PASS"  # Now using string literal instead of enum
        PART_NUMBER = "TEST-PCB-001"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW
        
        # Create run using new SDK syntax
        result = client.runs.create(
            outcome=OUTCOME,
            procedure_id=procedure_id,
            started_at=START_TIME,
            ended_at=END_TIME,
            serial_number=SERIAL_NUMBER,
            part_number=PART_NUMBER,
        )
        
        # Verify successful response
        assert_create_run_success(result)
        
        # Test runs.get method to get the created run with all details
        created_run = client.runs.get(id=result.id)
        
        # Verify all input parameters were saved correctly
        assert created_run.id == result.id
        assert created_run.outcome == "PASS"
        assert_timestamps_close(created_run.started_at, START_TIME)
        assert_timestamps_close(created_run.ended_at, END_TIME)
        assert created_run.unit is not None
        assert created_run.unit.serial_number == SERIAL_NUMBER
        assert created_run.unit.part.number == PART_NUMBER
        assert created_run.procedure.id == procedure_id
        
        # Also test runs.list to verify it's in the list
        list_result = client.runs.list(ids=[result.id])
        assert list_result.data
        assert len(list_result.data) == 1
        listed_run = list_result.data[0]
        assert listed_run.id == result.id
        assert listed_run.outcome == "PASS"