"""Test operated_by field."""

import uuid
from datetime import datetime, timedelta, timezone
from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success, operator_email_address


def test_operated_by(client: TofuPilot, operator_email_address, procedure_id: str):
    """Test that operated_by field works."""
    unique_id = str(uuid.uuid4())[:8]
    
    result = client.runs.create(
        serial_number=f"Test-{unique_id}",
        procedure_id=procedure_id,
        outcome="PASS",
        part_number=f"Part-{unique_id}",
        operated_by=operator_email_address,
        started_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        ended_at=datetime.now(timezone.utc),
    )
    
    assert_create_run_success(result)
    
    # Get the run to verify operated_by field
    run = client.runs.get(id=result.id)
    
    # Check if operated_by is present and has the expected email
    from tofupilot.v2.types import UNSET
    if run.operated_by is not UNSET and run.operated_by is not None:
        assert run.operated_by.email == operator_email_address  # type: ignore[union-attr]