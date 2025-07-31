"""Test deleting procedure versions with associated runs."""

import pytest
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from tests.v2.procedure_versions.utils import (
    assert_create_procedure_version_success,
)
from tests.v2.procedures.utils import assert_create_procedure_success
from tests.v2.utils import assert_create_run_success
from ...utils import assert_station_access_forbidden


def test_delete_procedure_version_with_runs(client: TofuPilot, auth_type: str) -> None:
    """Test that deleting procedure versions with runs is not allowed."""
    if auth_type == "station":
        # Stations cannot create procedures (HTTP 403 FORBIDDEN)
        with assert_station_access_forbidden("create procedure"):
            client.procedures.create(name="Test Procedure with Runs")
        return
    
    # Create a procedure
    procedure_result = client.procedures.create(name="Test Procedure with Runs")
    assert_create_procedure_success(procedure_result)
    
    # Create a procedure version
    version_result = client.procedures.versions.create(
        procedure_id=procedure_result.id,
        tag="v1.0.0"
    )
    assert_create_procedure_version_success(version_result)
    version_id = version_result.id
    
    # Create a run using this procedure version
    # The run will automatically create the unit
    now = datetime.now(timezone.utc)
    timestamp = now.strftime('%Y%m%d-%H%M%S-%f')
    run_result = client.runs.create(
        serial_number=f"TEST-UNIT-{timestamp}",
        procedure_id=procedure_result.id,
        procedure_version="v1.0.0",
        outcome="PASS",
        started_at=now,
        ended_at=now,
        part_number=f"PART-{timestamp}"
    )
    assert_create_run_success(run_result)
    
    # Try to delete the procedure version - should fail with 409 error
    from tofupilot.v2.errors import ErrorCONFLICT
    
    with pytest.raises(ErrorCONFLICT) as exc_info:
        client.procedures.versions.delete(
            procedure_id=procedure_result.id,
            tag="v1.0.0"
        )
    
    error_message = str(exc_info.value)
    assert "Cannot delete procedure version with associated runs" in error_message
    assert "1 runs" in error_message