"""Test getting individual procedure details."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_procedure_success, assert_get_procedure_success


class TestGetProcedure:
    """Test getting individual procedure details."""

    def test_get_procedure_by_id(self, client: TofuPilot, auth_type: str, procedure_id: str, timestamp: str) -> None:
        """Test getting a procedure by ID and verifying all fields."""
        if auth_type == "station":
            # Stations can get procedures — use the shared fixture
            result = client.procedures.get(id=procedure_id)
            assert_get_procedure_success(result)
            assert result.id == procedure_id
            return

        # Create a fresh procedure for isolation
        unique_id = str(uuid.uuid4())[:8]
        name = f"GetTest-{unique_id}-{timestamp}"
        create_result = client.procedures.create(name=name)
        assert_create_procedure_success(create_result)

        result = client.procedures.get(id=create_result.id)
        assert_get_procedure_success(result)

        assert result.id == create_result.id
        assert result.name == name
        assert result.created_at is not None
        assert isinstance(result.runs_count, (int, float))
        assert isinstance(result.recent_runs, list)
        assert isinstance(result.stations, list)

    def test_get_nonexistent_procedure(self, client: TofuPilot) -> None:
        """Test getting a procedure that doesn't exist."""
        with pytest.raises(ErrorNOTFOUND):
            client.procedures.get(id=str(uuid.uuid4()))

    def test_get_procedure_includes_recent_runs(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that get procedure includes recent_runs and stations."""
        result = client.procedures.get(id=procedure_id)
        assert_get_procedure_success(result)

        assert isinstance(result.recent_runs, list)
        assert isinstance(result.stations, list)

        for run in result.recent_runs:
            assert hasattr(run, 'id')
            assert hasattr(run, 'outcome')
            assert hasattr(run, 'started_at')
