"""Tests for TofuPilotClient.create_run() — Section 9a: Core Run Creation.

Covers POST /v1/runs with the direct Python client (no OpenHTF).
"""

import uuid
from datetime import datetime, timedelta, timezone

from tofupilot import TofuPilotClient


def test_minimal_pass_run(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """create_run with required fields and run_passed=True → PASS outcome."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"PASS-{uuid.uuid4().hex[:8]}"

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_pass"},
        run_passed=True,
        procedure_id=procedure_identifier,
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    check_run_exists(
        result["id"],
        serial_number=serial,
        part_number="test_cr_pass",
        outcome="PASS",
        procedure_id=procedure_id,
    )


def test_minimal_fail_run(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """create_run with run_passed=False → FAIL outcome."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"FAIL-{uuid.uuid4().hex[:8]}"

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_fail"},
        run_passed=False,
        procedure_id=procedure_identifier,
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    check_run_exists(
        result["id"],
        serial_number=serial,
        part_number="test_cr_fail",
        outcome="FAIL",
        procedure_id=procedure_id,
    )


def test_all_unit_fields_roundtrip(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """All UnitUnderTest fields preserved: serial_number, part_number, revision, batch_number (part_name is deprecated)."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"UUT-{uuid.uuid4().hex[:8]}"

    result = client.create_run(
        unit_under_test={
            "serial_number": serial,
            "part_number": "BOARD-X1",
            "revision": "C",
            "batch_number": "2024-0042",
        },
        run_passed=True,
        procedure_id=procedure_identifier,
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    check_run_exists(
        result["id"],
        serial_number=serial,
        part_number="BOARD-X1",
        revision="C",
        batch_number="2024-0042",
        procedure_id=procedure_id,
    )


def test_started_at_and_duration_preserved(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """started_at datetime and duration timedelta roundtrip on created run."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"TIME-{uuid.uuid4().hex[:8]}"

    started = datetime(2025, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
    dur = timedelta(minutes=2, seconds=30)

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_time"},
        run_passed=True,
        procedure_id=procedure_identifier,
        started_at=started,
        duration=dur,
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(
        result["id"],
        serial_number=serial,
        part_number="test_cr_time",
        procedure_id=procedure_id,
    )
    assert run.started_at is not None, "started_at should be set on created run"
    assert run.duration is not None, "duration should be set on created run"
