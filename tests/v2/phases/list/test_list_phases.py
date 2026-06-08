"""Test phases list filtering, pagination, and sorting (public V2 endpoint)."""

import uuid

from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success, get_random_test_dates


def _seed_run_with_phases(client: TofuPilot, procedure_id: str, part_number: str, serial: str):
    started_at, ended_at = get_random_test_dates()
    result = client.runs.create(
        serial_number=serial,
        procedure_id=procedure_id,
        part_number=part_number,
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "Power",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
            },
            {
                "name": "Report",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
            },
        ],
    )
    assert_create_run_success(result)
    return result.id


class TestListPhases:
    """Test phases list filtering, pagination, and sorting."""

    def test_list_returns_phases_for_run(self, client: TofuPilot, procedure_id: str) -> None:
        """Phases created with a run are returned, filtered to that run by id."""
        unique_id = str(uuid.uuid4())[:8]
        run_id = _seed_run_with_phases(
            client, procedure_id, f"PART-PH-{unique_id}", f"SN-PH-{unique_id}"
        )

        result = client.phases.list(procedure_id=procedure_id, ids=[run_id])
        assert len(result.data) == 2
        assert all(p.run_id == run_id for p in result.data)
        assert {p.name for p in result.data} == {"Power", "Report"}

    def test_outcome_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """The phase outcome filter narrows to matching phases."""
        unique_id = str(uuid.uuid4())[:8]
        run_id = _seed_run_with_phases(
            client, procedure_id, f"PART-PHO-{unique_id}", f"SN-PHO-{unique_id}"
        )

        result = client.phases.list(procedure_id=procedure_id, ids=[run_id], outcomes=["FAIL"])
        assert len(result.data) == 1
        assert result.data[0].name == "Report"
        assert result.data[0].outcome == "FAIL"

    def test_limit_and_cursor_pagination(self, client: TofuPilot, procedure_id: str) -> None:
        """limit caps the page and next_cursor walks the result set."""
        unique_id = str(uuid.uuid4())[:8]
        run_id = _seed_run_with_phases(
            client, procedure_id, f"PART-PHP-{unique_id}", f"SN-PHP-{unique_id}"
        )

        page1 = client.phases.list(procedure_id=procedure_id, ids=[run_id], limit=1)
        assert len(page1.data) == 1
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None

        page2 = client.phases.list(
            procedure_id=procedure_id, ids=[run_id], limit=1, cursor=page1.meta.next_cursor
        )
        assert len(page2.data) == 1
        assert page1.data[0].id != page2.data[0].id
