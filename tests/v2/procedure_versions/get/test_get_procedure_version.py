"""Test getting procedure versions."""

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError
from tests.v2.procedure_versions.utils import (
    assert_create_procedure_version_success,
    assert_get_procedure_version_success,
)
from tests.v2.procedures.utils import assert_create_procedure_success
from tofupilot.v2.errors import ErrorNOTFOUND
from ...utils import assert_station_access_forbidden


def test_get_procedure_version(client: TofuPilot, auth_type: str) -> None:
    """Test getting a procedure version by ID."""
    if auth_type == "station":
        # Stations cannot create procedures (HTTP 403 FORBIDDEN)
        with assert_station_access_forbidden("create procedure"):
            client.procedures.create(name="Test Procedure for Get")
        return
    
    # Create a procedure
    procedure_result = client.procedures.create(name="Test Procedure for Get")
    assert_create_procedure_success(procedure_result)
    procedure_id = procedure_result.id
    
    # Create a procedure version
    version_result = client.procedures.versions.create(
        procedure_id=procedure_id,
        tag="v1.0.0"
    )
    assert_create_procedure_version_success(version_result)
    
    # Get the version
    version = client.procedures.versions.get(
        procedure_id=procedure_id,
        tag="v1.0.0"
    )
    assert_get_procedure_version_success(version)
    
    # Verify details
    assert version.id == version_result.id
    assert version.tag == "v1.0.0"
    assert version.procedure.id == procedure_id
    assert version.procedure.name == "Test Procedure for Get"
    assert version.run_count == 0
    assert version.created_at is not None


def test_get_nonexistent_procedure_version(client: TofuPilot, auth_type: str) -> None:
    """Test getting a non-existent procedure version."""
    if auth_type == "station":
        # Stations cannot create procedures (HTTP 403 FORBIDDEN)
        with assert_station_access_forbidden("create procedure"):
            client.procedures.create(name="Test Procedure for Nonexistent Version")
        return
    
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    # Create a dummy procedure for this test
    procedure_result = client.procedures.create(name="Test Procedure for Nonexistent Version")
    procedure_id = procedure_result.id
    
    with pytest.raises(ErrorNOTFOUND) as exc_info:
        client.procedures.versions.get(
            procedure_id=procedure_id,
            tag="nonexistent-tag"
        )
    
    error_message = str(exc_info.value)
    assert "Procedure version not found" in error_message


def test_get_invalid_procedure_version_id(client: TofuPilot, auth_type: str) -> None:
    """Test getting a procedure version with invalid ID format."""
    with pytest.raises(APIError) as exc_info:
        client.procedures.versions.get(
            procedure_id="invalid-uuid",
            tag="v1.0.0"
        )
    
    error = exc_info.value
    assert error.status_code == 400