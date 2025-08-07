"""Test deleting procedure versions."""

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND, APIError
from tests.v2.procedure_versions.utils import (
    assert_create_procedure_version_success,
    assert_delete_procedure_version_success,
)
from tests.v2.procedures.utils import assert_create_procedure_success
from tests.v2.utils import assert_station_access_forbidden


def test_delete_procedure_version(client: TofuPilot, auth_type: str, procedure_id: str, timestamp) -> None:
    """Test deleting a procedure version."""
    if auth_type == "station":
        # Stations cannot delete procedure versions (HTTP 403 FORBIDDEN)
        from datetime import datetime, timezone
        
        # Create a procedure version as a station first
        version_result = client.procedures.versions.create(
            procedure_id=procedure_id,
            tag=f"v-station-test-{timestamp}"
        )
        assert_create_procedure_version_success(version_result)
        version_id = version_result.id
        
        # Stations cannot delete procedure versions
        with assert_station_access_forbidden("delete procedure version"):
            client.procedures.versions.delete(
                procedure_id=procedure_id,
                tag=f"v-station-test-{timestamp}"
            )
        return
    
    # Create a procedure
    procedure_result = client.procedures.create(name="Test Procedure for Delete")
    assert_create_procedure_success(procedure_result)
    procedure_id = procedure_result.id
    
    # Create a procedure version
    version_result = client.procedures.versions.create(
        procedure_id=procedure_id,
        tag="v1.0.0"
    )
    assert_create_procedure_version_success(version_result)
    version_id = version_result.id
    
    # Verify it exists
    version = client.procedures.versions.get(
        procedure_id=procedure_id,
        tag="v1.0.0"
    )
    assert version.id == version_id
    
    # Delete the version
    delete_result = client.procedures.versions.delete(
        procedure_id=procedure_id,
        tag="v1.0.0"
    )
    assert_delete_procedure_version_success(delete_result)
    assert delete_result.id == version_id
    
    # Verify it's deleted
    with pytest.raises(ErrorNOTFOUND) as exc_info:
        client.procedures.versions.get(
            procedure_id=procedure_id,
            tag="v1.0.0"
        )
    
    error_message = str(exc_info.value)
    assert "Procedure version not found" in error_message


def test_delete_nonexistent_procedure_version(client: TofuPilot, auth_type: str, procedure_id: str) -> None:
    """Test deleting a non-existent procedure version."""
    if auth_type == "station":
        # Stations cannot delete procedure versions (HTTP 403 FORBIDDEN)
        with assert_station_access_forbidden("delete procedure version"):
            client.procedures.versions.delete(
                procedure_id=procedure_id,
                tag="nonexistent"
            )
        return
    
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    with pytest.raises(ErrorNOTFOUND) as exc_info:
        client.procedures.versions.delete(
            procedure_id=procedure_id,
            tag="nonexistent"
        )
    
    error_message = str(exc_info.value)
    assert "Procedure version not found" in error_message


def test_delete_invalid_procedure_version_id(client: TofuPilot, auth_type: str, procedure_id: str) -> None:
    """Test deleting with invalid ID format."""
    if auth_type == "station":
        # Stations cannot delete procedure versions (HTTP 403 FORBIDDEN)
        with assert_station_access_forbidden("delete procedure version"):
            client.procedures.versions.delete(
                procedure_id="invalid-uuid",
                tag="v1.0.0"
            )
        return
    
    with pytest.raises(APIError) as exc_info:
        client.procedures.versions.delete(
            procedure_id="invalid-uuid",
            tag="v1.0.0"
        )
    
    error = exc_info.value
    assert error.status_code == 400
    assert "Invalid uuid" in str(error)