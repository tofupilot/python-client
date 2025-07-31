"""Test minimal procedure version creation."""

import pytest
from tofupilot.v2 import TofuPilot
from tests.v2.procedure_versions.utils import (
    assert_create_procedure_version_success,
)
from tests.v2.procedures.utils import assert_create_procedure_success
from tests.v2.utils import assert_station_access_forbidden


def test_minimal_procedure_version_create(client: TofuPilot, auth_type: str) -> None:
    """Test creating a procedure version with minimal required fields."""
    if auth_type == "user":
        # First create a procedure
        procedure_result = client.procedures.create(name="Test Procedure for Version")
        assert_create_procedure_success(procedure_result)
        procedure_id = procedure_result.id
        
        # Create a procedure version
        result = client.procedures.versions.create(
            procedure_id=procedure_id,
            tag="v1.0.0"
        )
        
        assert_create_procedure_version_success(result)
        
        # Verify the version was created  
        version = client.procedures.versions.get(
            procedure_id=procedure_id,
            tag="v1.0.0"
        )
        assert version.id == result.id
        assert version.tag == "v1.0.0"
        assert version.procedure.id == procedure_id
        assert version.run_count == 0
    else:
        # Stations cannot create procedures (HTTP 403 FORBIDDEN)
        with assert_station_access_forbidden("create procedure"):
            client.procedures.create(name="Test Procedure for Version")