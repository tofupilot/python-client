"""Test deleting runs."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ...utils import (
    assert_create_run_success,
    assert_delete_run_success,
    assert_station_access_forbidden,
    get_random_test_dates,
)


class TestDeleteRun:
    """Test deleting runs."""

    def test_delete_single_run(self, client: TofuPilot, auth_type: str, procedure_id: str) -> None:
        """Test deleting a single run by ID and verifying it's gone."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete run"):
                client.runs.delete(ids=[str(uuid.uuid4())])
            return

        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]

        create_result = client.runs.create(
            serial_number=f"SN-DEL-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-DEL-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        delete_result = client.runs.delete(ids=[create_result.id])
        assert_delete_run_success(delete_result)
        assert create_result.id in delete_result.ids

        with pytest.raises(ErrorNOTFOUND):
            client.runs.get(id=create_result.id)

    def test_delete_multiple_runs(self, client: TofuPilot, auth_type: str, procedure_id: str) -> None:
        """Test deleting multiple runs at once."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete runs"):
                client.runs.delete(ids=[str(uuid.uuid4())])
            return

        run_ids = []
        for i in range(3):
            started_at, ended_at = get_random_test_dates()
            unique_id = str(uuid.uuid4())[:8]

            result = client.runs.create(
                serial_number=f"SN-DEL-MULTI-{i}-{unique_id}",
                procedure_id=procedure_id,
                part_number=f"PART-DEL-MULTI-{unique_id}",
                started_at=started_at,
                outcome="PASS",
                ended_at=ended_at,
            )
            assert_create_run_success(result)
            run_ids.append(result.id)

        delete_result = client.runs.delete(ids=run_ids)
        assert_delete_run_success(delete_result)

        for run_id in run_ids:
            assert run_id in delete_result.ids
            with pytest.raises(ErrorNOTFOUND):
                client.runs.get(id=run_id)

    def test_delete_nonexistent_run(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting a run that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete nonexistent run"):
                client.runs.delete(ids=[str(uuid.uuid4())])
            return

        nonexistent_id = str(uuid.uuid4())

        with pytest.raises(ErrorNOTFOUND):
            client.runs.delete(ids=[nonexistent_id])

    def test_delete_run_twice(self, client: TofuPilot, auth_type: str, procedure_id: str) -> None:
        """Test deleting the same run twice (second should fail)."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete run twice"):
                client.runs.delete(ids=[str(uuid.uuid4())])
            return

        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]

        create_result = client.runs.create(
            serial_number=f"SN-DEL-TWICE-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-DEL-TWICE-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        client.runs.delete(ids=[create_result.id])

        with pytest.raises(ErrorNOTFOUND):
            client.runs.delete(ids=[create_result.id])
