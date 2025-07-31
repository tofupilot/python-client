"""Test logs saving in run creation."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List
from tofupilot.v2 import TofuPilot
from tofupilot.v2.models import RunCreateLog
from ...utils import assert_create_run_success


def test_run_with_logs(client: TofuPilot, procedure_id: str) -> None:
    """Test that runs with logs are properly saved."""
    # Generate unique identifiers for this test
    unique_id = str(uuid.uuid4())[:8]
    SERIAL_NUMBER = f"TestUnit-Logs-{unique_id}"
    PART_NUMBER = f"TestPart-Logs-{unique_id}"
    REVISION_NUMBER = f"Rev-Logs-{unique_id}"
    
    OUTCOME = "PASS"
    NOW = datetime.now(timezone.utc)
    START_TIME = NOW - timedelta(minutes=5)
    END_TIME = NOW

    # Define logs array with type annotation
    logs: List[RunCreateLog] = [
        RunCreateLog(
            level="INFO",
            timestamp=START_TIME,
            message="Starting PCB functional test",
            source_file="pcb_test.py",
            line_number=25
        ),
        RunCreateLog(
            level="DEBUG",
            timestamp=START_TIME + timedelta(seconds=10),
            message="Reading voltage: 3.3V",
            source_file="voltage_measurement.py",
            line_number=89
        ),
        RunCreateLog(
            level="WARNING",
            timestamp=START_TIME + timedelta(seconds=15),
            message="Temperature higher than expected: 45°C",
            source_file="temperature_monitor.py",
            line_number=123
        ),
        RunCreateLog(
            level="INFO",
            timestamp=START_TIME + timedelta(seconds=20),
            message="All functional tests passed",
            source_file="pcb_test.py",
            line_number=156
        )
    ]

    # Create run with logs
    result = client.runs.create(
        serial_number=SERIAL_NUMBER,
        procedure_id=procedure_id,
        outcome=OUTCOME,
        part_number=PART_NUMBER,
        revision_number=REVISION_NUMBER,
        logs=logs,
        started_at=START_TIME,
        ended_at=END_TIME,
    )
    
    assert_create_run_success(result)
    
    # Get the created run details with logs included
    run = client.runs.get(id=result.id)
    
    # Verify logs were saved properly
    assert run.logs is not None
    assert len(run.logs) == len(logs)
    
    # Check each log matches the input data
    for output_log, input_log in zip(run.logs, logs):
        assert output_log.level == input_log.level
        assert output_log.message == input_log.message
        assert output_log.source_file == input_log.source_file
        assert output_log.line_number == input_log.line_number
        # Check that an ID was generated
        assert hasattr(output_log, 'id') and output_log.id
        # Verify timestamp is preserved (allowing small differences)
        assert abs((output_log.timestamp - input_log.timestamp).total_seconds()) < 1