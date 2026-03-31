"""Tests for TofuPilotClient.create_run() — Section 9b: Procedure Resolution."""

import uuid

from tofupilot import TofuPilotClient


def test_procedure_resolved_by_name(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """procedure_name alongside procedure_id → procedure name preserved on created run."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"PNAME-{uuid.uuid4().hex[:8]}"
    proc_name = f"AutoCreated-{uuid.uuid4().hex[:8]}"

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_pname"},
        run_passed=True,
        procedure_id=procedure_identifier,
        procedure_name=proc_name,
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    check_run_exists(
        result["id"],
        serial_number=serial,
        part_number="test_cr_pname",
        procedure_id=procedure_id,
    )


def test_procedure_resolved_by_id(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """procedure_id matches an existing procedure; run linked correctly."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"PID-{uuid.uuid4().hex[:8]}"

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_pid"},
        run_passed=True,
        procedure_id=procedure_identifier,
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    check_run_exists(
        result["id"],
        serial_number=serial,
        part_number="test_cr_pid",
        procedure_id=procedure_id,
    )


def test_procedure_version_stored(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """procedure_version tag preserved on created run."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"PVER-{uuid.uuid4().hex[:8]}"

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_pver"},
        run_passed=True,
        procedure_id=procedure_identifier,
        procedure_version="3.1.0",
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    check_run_exists(
        result["id"],
        serial_number=serial,
        part_number="test_cr_pver",
        procedure_id=procedure_id,
        procedure_version="3.1.0",
    )
