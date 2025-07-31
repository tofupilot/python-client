"""Test simple procedure version creation using existing procedure."""

import uuid
from tofupilot.v2 import TofuPilot
from tests.v2.procedure_versions.utils import (
    assert_create_procedure_version_success,
)


def test_procedure_version_create_with_existing_procedure(client: TofuPilot, procedure_id: str) -> None:
    """Test creating a procedure version using existing procedure_id fixture."""
    # Create a procedure version for the existing procedure
    version_value = f"v1.0.0-test-{uuid.uuid4().hex[:8]}"
    result = client.procedures.versions.create(
        procedure_id=procedure_id,
        tag=version_value
    )
    
    assert_create_procedure_version_success(result)
    
    # Verify the version was created
    version = client.procedures.versions.get(procedure_id=procedure_id, tag=version_value)
    assert version.id == result.id
    assert version.tag == version_value
    assert version.procedure.id == procedure_id
    assert version.run_count == 0