"""Test procedure version creation validation."""

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError, ErrorNOTFOUND
from tests.v2.procedures.utils import assert_create_procedure_success
from ...utils import assert_station_access_forbidden


def test_create_version_empty_name(client: TofuPilot, auth_type: str) -> None:
    """Test creating a procedure version with empty name."""
    if auth_type == "station":
        # Stations cannot create procedures (HTTP 403 FORBIDDEN)
        with assert_station_access_forbidden("create procedure"):
            client.procedures.create(name="Test Procedure")
        return
    
    # Create a procedure first
    procedure_result = client.procedures.create(name="Test Procedure")
    assert_create_procedure_success(procedure_result)
    
    with pytest.raises(APIError) as exc_info:
        client.procedures.versions.create(
            procedure_id=procedure_result.id,
            tag=""
        )
    
    error = exc_info.value
    assert error.status_code == 400
    assert "tag" in str(error).lower() or "name" in str(error).lower()


def test_create_version_long_name(client: TofuPilot, auth_type: str) -> None:
    """Test creating a procedure version with name exceeding max length."""
    if auth_type == "station":
        # Stations cannot create procedures (HTTP 403 FORBIDDEN)
        with assert_station_access_forbidden("create procedure"):
            client.procedures.create(name="Test Procedure")
        return
    
    # Create a procedure first
    procedure_result = client.procedures.create(name="Test Procedure")
    assert_create_procedure_success(procedure_result)
    
    with pytest.raises(APIError) as exc_info:
        client.procedures.versions.create(
            procedure_id=procedure_result.id,
            tag="v" * 61  # Exceeds 60 character limit
        )
    
    error = exc_info.value
    assert error.status_code == 400
    assert "60 character" in str(error)


def test_create_version_invalid_procedure_id(client: TofuPilot, auth_type: str) -> None:
    """Test creating a procedure version with invalid procedure ID."""
    with pytest.raises(APIError) as exc_info:
        client.procedures.versions.create(
            procedure_id="invalid-uuid",
            tag="v1.0.0"
        )
    
    error = exc_info.value
    assert error.status_code == 400 or error.status_code == 404


def test_create_version_nonexistent_procedure(client: TofuPilot, auth_type: str) -> None:
    """Test creating a procedure version for non-existent procedure."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"

    if auth_type == "station":
        with assert_station_access_forbidden("create version for nonexistent procedure"):
            client.procedures.versions.create(
                procedure_id=fake_uuid,
                tag="v1.0.0"
            )
        return

    with pytest.raises(ErrorNOTFOUND) as exc_info:
        client.procedures.versions.create(
            procedure_id=fake_uuid,
            tag="v1.0.0"
        )

    error = exc_info.value
    assert "procedure" in str(error.data.message).lower()