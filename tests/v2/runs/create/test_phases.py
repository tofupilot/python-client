"""Test phases saving in run creation."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List
from tofupilot.v2 import TofuPilot
from tofupilot.v2.models import RunCreatePhase
from ...utils import assert_create_run_success


def test_run_with_phases(client: TofuPilot, procedure_id: str) -> None:
    """Test that runs with phases are properly saved."""
    # Generate unique identifiers for this test
    unique_id = str(uuid.uuid4())[:8]
    SERIAL_NUMBER = f"TestUnit-Phases-{unique_id}"
    PART_NUMBER = f"TestPart-Phases-{unique_id}"
    REVISION_NUMBER = f"Rev-Phases-{unique_id}"
    
    OUTCOME = "PASS"
    NOW = datetime.now(timezone.utc)
    START_TIME = NOW - timedelta(minutes=10)
    END_TIME = NOW

    # Define phases array with type annotation
    phases: List[RunCreatePhase] = [
        RunCreatePhase(
            name="Power-On Self Test",
            outcome="PASS",
            started_at=START_TIME,
            ended_at=START_TIME + timedelta(minutes=2)
        ),
        RunCreatePhase(
            name="Voltage Calibration",
            outcome="PASS",
            started_at=START_TIME + timedelta(minutes=2),
            ended_at=START_TIME + timedelta(minutes=5)
        ),
        RunCreatePhase(
            name="Functional Test",
            outcome="PASS",
            started_at=START_TIME + timedelta(minutes=5),
            ended_at=START_TIME + timedelta(minutes=8)
        ),
        RunCreatePhase(
            name="Burn-in Test",
            outcome="PASS",
            started_at=START_TIME + timedelta(minutes=8),
            ended_at=END_TIME
        )
    ]

    # Create run with phases
    result = client.runs.create(
        serial_number=SERIAL_NUMBER,
        procedure_id=procedure_id,
        outcome=OUTCOME,
        part_number=PART_NUMBER,
        revision_number=REVISION_NUMBER,
        phases=phases,
        started_at=START_TIME,
        ended_at=END_TIME,
    )
    
    assert_create_run_success(result)
    
    # Get the created run details with phases included
    run = client.runs.get(id=result.id)
    
    # Verify phases were saved properly
    assert run.phases is not None
    assert len(run.phases) == len(phases)
    
    # Check each phase matches the input data
    for output_phase, input_phase in zip(run.phases, phases):
        assert hasattr(output_phase, 'name') and output_phase.name == input_phase.name
        assert hasattr(output_phase, 'outcome') and output_phase.outcome == input_phase.outcome
        # Check that timestamps are preserved (allowing small differences)
        assert hasattr(output_phase, 'started_at')
        assert abs((output_phase.started_at - input_phase.started_at).total_seconds()) < 1
        assert hasattr(output_phase, 'ended_at')
        assert abs((output_phase.ended_at - input_phase.ended_at).total_seconds()) < 1
        # Check that an ID was generated if the model exposes it
        if hasattr(output_phase, 'id'):
            assert output_phase.id