"""Tests for TofuPilotClient.create_run() — Section 9f: Sub-units (direct)."""

import uuid
from datetime import datetime, timedelta, timezone

import tofupilot.v2
from tofupilot import TofuPilotClient


def test_sub_units_linked_to_run(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """sub_units=[{"serial_number": "..."}] → sub-unit linkage verified on created run."""
    unique_id = uuid.uuid4().hex[:8]
    sub_serial = f"SUB-{unique_id}"
    serial = f"PARENT-{unique_id}"

    # Sub-unit must already exist — create it via V2
    v2_client = tofupilot.v2.TofuPilot(
        api_key=api_key,
        server_url=f"{tofupilot_server_url}/api",
    )
    now = datetime.now(timezone.utc)
    v2_client.runs.create(
        serial_number=sub_serial,
        procedure_id=procedure_id,
        outcome="PASS",
        part_number="test_cr_sub_child",
        started_at=now - timedelta(minutes=5),
        ended_at=now,
    )

    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_sub"},
        run_passed=True,
        procedure_id=procedure_identifier,
        sub_units=[{"serial_number": sub_serial}],
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(result["id"], serial_number=serial, procedure_id=procedure_id)

    assert run.sub_units, "Expected sub_units on created run"
    sub_serials = [su.serial_number for su in run.sub_units]
    assert sub_serial in sub_serials
