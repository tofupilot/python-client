"""Test deleting procedure versions."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import (
    assert_create_procedure_version_success,
    assert_delete_procedure_version_success,
)
from ...procedures.utils import assert_create_procedure_success
from ...utils import assert_station_access_forbidden


class TestDeleteProcedureVersion:
    """Test deleting procedure versions."""

    def test_delete_version(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test deleting a procedure version and verifying it's gone."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete procedure version"):
                client.procedures.versions.delete(
                    procedure_id=str(uuid.uuid4()),
                    tag="v1.0.0",
                )
            return

        # Create procedure + version
        unique_id = str(uuid.uuid4())[:8]
        procedure = client.procedures.create(name=f"DeleteVersionTest-{unique_id}-{timestamp}")
        assert_create_procedure_success(procedure)

        tag = f"v1.0.0-{unique_id}"
        version = client.procedures.versions.create(procedure_id=procedure.id, tag=tag)
        assert_create_procedure_version_success(version)

        # Delete it
        delete_result = client.procedures.versions.delete(procedure_id=procedure.id, tag=tag)
        assert_delete_procedure_version_success(delete_result)
        assert delete_result.id == version.id

        # Verify it's gone
        with pytest.raises(ErrorNOTFOUND):
            client.procedures.versions.get(procedure_id=procedure.id, tag=tag)

    def test_delete_nonexistent_version(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test deleting a version with a tag that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete nonexistent procedure version"):
                client.procedures.versions.delete(
                    procedure_id=str(uuid.uuid4()),
                    tag="nonexistent-tag",
                )
            return

        # Create a real procedure so the 404 is specifically about the tag
        unique_id = str(uuid.uuid4())[:8]
        procedure = client.procedures.create(name=f"DeleteVersionNotFound-{unique_id}-{timestamp}")
        assert_create_procedure_success(procedure)

        with pytest.raises(ErrorNOTFOUND):
            client.procedures.versions.delete(
                procedure_id=procedure.id,
                tag="nonexistent-tag",
            )
