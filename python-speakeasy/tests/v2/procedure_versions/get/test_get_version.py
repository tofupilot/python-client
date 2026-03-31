"""Test getting procedure versions."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import (
    assert_create_procedure_version_success,
    assert_get_procedure_version_success,
)
from ...procedures.utils import assert_create_procedure_success


class TestGetProcedureVersion:
    """Test getting procedure versions by tag."""

    def test_get_version_by_tag(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test getting a procedure version by tag and verifying all fields."""
        if auth_type == "station":
            # Stations can read versions — but can't create procedures/versions to set up test data.
            # Just verify a get on a nonexistent version returns 404.
            with pytest.raises(ErrorNOTFOUND):
                client.procedures.versions.get(
                    procedure_id=str(uuid.uuid4()),
                    tag="v1.0.0",
                )
            return

        # Create procedure + version
        unique_id = str(uuid.uuid4())[:8]
        procedure = client.procedures.create(name=f"GetVersionTest-{unique_id}-{timestamp}")
        assert_create_procedure_success(procedure)

        tag = f"v1.0.0-{unique_id}"
        version = client.procedures.versions.create(procedure_id=procedure.id, tag=tag)
        assert_create_procedure_version_success(version)

        # Get it back
        result = client.procedures.versions.get(procedure_id=procedure.id, tag=tag)
        assert_get_procedure_version_success(result)

        assert result.id == version.id
        assert result.tag == tag
        assert result.created_at is not None
        assert result.procedure.id == procedure.id
        assert isinstance(result.run_count, int)

    def test_get_nonexistent_version(self, client: TofuPilot, auth_type: str, procedure_id: str) -> None:
        """Test getting a version with a tag that doesn't exist."""
        if auth_type == "station":
            with pytest.raises(ErrorNOTFOUND):
                client.procedures.versions.get(
                    procedure_id=procedure_id,
                    tag="nonexistent-tag",
                )
            return

        # Create a real procedure so the 404 is specifically about the tag
        unique_id = str(uuid.uuid4())[:8]
        procedure = client.procedures.create(name=f"GetVersionNotFound-{unique_id}")
        assert_create_procedure_success(procedure)

        with pytest.raises(ErrorNOTFOUND):
            client.procedures.versions.get(
                procedure_id=procedure.id,
                tag="nonexistent-tag",
            )
