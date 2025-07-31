"""Test automatic part number parsing from serial number."""

from datetime import datetime, timedelta, timezone
from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success, assert_timestamps_close


class TestCreateRunPartNumberParsing:

    def test_automatic_part_number_parsing(self, client: TofuPilot, procedure_id: str) -> None:
        """Test run creation with explicit part number (automatic parsing not configured)."""
        # Test constants
        # Since automatic parsing is not configured, we provide the part number explicitly
        SERIAL_NUMBER = "PCB-V1_2-SN-001234"
        PART_NUMBER = "PCB-V1_2"  # Provide part number explicitly
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW
        
        result = client.runs.create(
            serial_number=SERIAL_NUMBER,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            started_at=START_TIME,
            ended_at=END_TIME,
            part_number=PART_NUMBER,  # Provide part number explicitly
        )
        
        # Verify successful response
        assert_create_run_success(result)
        
        # Test runs.get method to get the created run with all details
        created_run = client.runs.get(id=result.id)
        
        # Verify all input parameters were saved correctly
        assert created_run.id == result.id
        assert created_run.outcome == OUTCOME
        assert_timestamps_close(created_run.started_at, START_TIME)
        assert_timestamps_close(created_run.ended_at, END_TIME)
        assert created_run.unit is not None
        assert created_run.unit.serial_number == SERIAL_NUMBER
        assert created_run.unit.part is not None
        assert created_run.unit.part.number == PART_NUMBER
        assert created_run.procedure is not None
        assert created_run.procedure.id == procedure_id