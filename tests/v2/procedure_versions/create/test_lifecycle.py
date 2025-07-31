"""Test procedure version lifecycle operations."""

from typing import List
import pytest
from tofupilot.v2 import TofuPilot
from tests.v2.procedure_versions.utils import (
    assert_create_procedure_version_success,
)
from tests.v2.procedures.utils import assert_create_procedure_success
from ...utils import assert_station_access_forbidden


def test_procedure_version_lifecycle(client: TofuPilot, auth_type: str) -> None:
    """Test complete lifecycle of procedure version: create and get."""
    if auth_type == "station":
        # Stations cannot create procedures (HTTP 403 FORBIDDEN)
        with assert_station_access_forbidden("create procedure"):
            client.procedures.create(name="Test Procedure for Lifecycle")
        return
    
    # Create a procedure first
    procedure_result = client.procedures.create(name="Test Procedure for Lifecycle")
    assert_create_procedure_success(procedure_result)
    procedure_id = procedure_result.id
    
    # Create multiple versions
    version_names = ["v1.0.0", "v1.1.0", "v2.0.0"]
    created_versions: List[str] = []
    
    for name in version_names:
        result = client.procedures.versions.create(
            procedure_id=procedure_id,
            tag=name
        )
        assert_create_procedure_version_success(result)
        created_versions.append(result.id)
    
    # Verify we can get the procedure
    procedure = client.procedures.get(id=procedure_id)
    assert procedure.id == procedure_id
    
    # Get each version individually by tag
    for i, tag in enumerate(version_names):
        version = client.procedures.versions.get(
            procedure_id=procedure_id,
            tag=tag
        )
        assert version.id == created_versions[i]
        assert version.tag == tag
        assert version.procedure.id == procedure_id
        assert version.run_count == 0