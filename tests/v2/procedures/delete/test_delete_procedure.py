"""Test deleting procedures."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_procedure_success, assert_delete_procedure_success
from ...utils import assert_station_access_forbidden


class TestDeleteProcedure:
    """Test deleting procedures."""

    def test_delete_procedure(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test deleting a procedure and verifying it's gone."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete procedure"):
                client.procedures.delete(id=str(uuid.uuid4()))
            return

        # Create a procedure to delete
        unique_id = str(uuid.uuid4())[:8]
        name = f"DeleteTest-{unique_id}-{timestamp}"
        create_result = client.procedures.create(name=name)
        assert_create_procedure_success(create_result)

        # Delete it
        delete_result = client.procedures.delete(id=create_result.id)
        assert_delete_procedure_success(delete_result)
        assert delete_result.id == create_result.id

        # Verify it's gone
        with pytest.raises(ErrorNOTFOUND):
            client.procedures.get(id=create_result.id)

    def test_delete_nonexistent_procedure(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting a procedure that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete nonexistent procedure"):
                client.procedures.delete(id=str(uuid.uuid4()))
            return

        with pytest.raises(ErrorNOTFOUND):
            client.procedures.delete(id=str(uuid.uuid4()))
