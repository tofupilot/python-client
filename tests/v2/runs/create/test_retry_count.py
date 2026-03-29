"""Test retry_count field on phases."""

import uuid
from tofupilot.v2 import TofuPilot
from ...utils import get_random_test_dates, assert_create_run_success


def test_retry_count_stored_and_returned(client: TofuPilot, procedure_id: str):
    """Phases with explicit retry_count are stored and returned correctly."""
    started_at, ended_at = get_random_test_dates()
    uid = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-RETRY-{uid}",
        procedure_id=procedure_id,
        part_number=f"PART-RETRY-{uid}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "check_voltage",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "retry_count": 0,
            },
            {
                "name": "check_voltage",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "retry_count": 1,
            },
            {
                "name": "check_voltage",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "retry_count": 2,
            },
        ],
    )
    assert_create_run_success(result)

    run = client.runs.get(id=result.id)
    assert run.phases is not None
    assert len(run.phases) == 3
    assert run.phases[0].retry_count == 0
    assert run.phases[1].retry_count == 1
    assert run.phases[2].retry_count == 2


def test_retry_count_defaults_to_zero(client: TofuPilot, procedure_id: str):
    """Phases without retry_count default to 0."""
    started_at, ended_at = get_random_test_dates()
    uid = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-RETRY-DEF-{uid}",
        procedure_id=procedure_id,
        part_number=f"PART-RETRY-DEF-{uid}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "simple_phase",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
            },
        ],
    )
    assert_create_run_success(result)

    run = client.runs.get(id=result.id)
    assert run.phases is not None
    assert len(run.phases) == 1
    assert run.phases[0].retry_count == 0
