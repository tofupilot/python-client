"""Test logs list filtering, pagination, and sorting (public V2 endpoint)."""

import uuid

from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success, get_random_test_dates


def _seed_run_with_logs(client: TofuPilot, procedure_id: str, part_number: str, serial: str):
    started_at, ended_at = get_random_test_dates()
    result = client.runs.create(
        serial_number=serial,
        procedure_id=procedure_id,
        part_number=part_number,
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        logs=[
            {
                "level": "INFO",
                "timestamp": started_at,
                "message": "Test execution started",
                "source_file": "main.py",
                "line_number": 10,
            },
            {
                "level": "ERROR",
                "timestamp": started_at,
                "message": "Sensor read failed",
                "source_file": "sensor.py",
                "line_number": 42,
            },
        ],
    )
    assert_create_run_success(result)
    return result.id


class TestListLogs:
    """Test logs list filtering, pagination, and sorting."""

    def test_list_returns_logs_for_run(self, client: TofuPilot, procedure_id: str) -> None:
        """Logs created with a run are returned by the list endpoint, filtered by run."""
        unique_id = str(uuid.uuid4())[:8]
        run_id = _seed_run_with_logs(
            client, procedure_id, f"PART-LOGS-{unique_id}", f"SN-LOGS-{unique_id}"
        )

        result = client.logs.list(run_ids=[run_id])
        assert len(result.data) == 2
        assert all(log.run.id == run_id for log in result.data)
        levels = {log.level for log in result.data}
        assert levels == {"INFO", "ERROR"}

    def test_level_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """The level filter narrows results to the requested levels."""
        unique_id = str(uuid.uuid4())[:8]
        run_id = _seed_run_with_logs(
            client, procedure_id, f"PART-LVL-{unique_id}", f"SN-LVL-{unique_id}"
        )

        result = client.logs.list(run_ids=[run_id], levels=["ERROR"])
        assert len(result.data) == 1
        assert result.data[0].level == "ERROR"
        assert result.data[0].message == "Sensor read failed"

    def test_limit_and_cursor_pagination(self, client: TofuPilot, procedure_id: str) -> None:
        """limit caps the page and next_cursor walks the result set."""
        unique_id = str(uuid.uuid4())[:8]
        run_id = _seed_run_with_logs(
            client, procedure_id, f"PART-PAGE-{unique_id}", f"SN-PAGE-{unique_id}"
        )

        page1 = client.logs.list(run_ids=[run_id], limit=1)
        assert len(page1.data) == 1
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None

        page2 = client.logs.list(run_ids=[run_id], limit=1, cursor=page1.meta.next_cursor)
        assert len(page2.data) == 1
        assert page2.meta.has_more is False
        assert page1.data[0].id != page2.data[0].id
