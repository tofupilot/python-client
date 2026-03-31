"""Tests for TofuPilotClient.get_runs() — Section 10: GET /v1/runs."""

import uuid

from tofupilot import TofuPilotClient


def _create_run(client, serial, procedure_id, passed=True):
    return client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_gr"},
        run_passed=passed,
        procedure_id=procedure_id,
    )


def test_returns_run_for_known_serial(
    tofupilot_server_url, api_key, procedure_identifier
):
    """Create a run, then get_runs(serial_number) → result contains the run."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"GR1-{uuid.uuid4().hex[:8]}"

    created = _create_run(client, serial, procedure_identifier)
    assert created.get("id")

    result = client.get_runs(serial)
    assert result["success"] is True
    run_ids = [r["id"] for r in result["result"]]
    assert created["id"] in run_ids


def test_response_structure(
    tofupilot_server_url, api_key, procedure_identifier
):
    """Response has success, result list with run objects containing expected keys."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"GR2-{uuid.uuid4().hex[:8]}"

    _create_run(client, serial, procedure_identifier)

    result = client.get_runs(serial)
    assert result["success"] is True
    assert isinstance(result["result"], list)
    assert len(result["result"]) >= 1

    run = result["result"][0]
    assert "id" in run
    assert "outcome" in run
    assert "unit" in run
    assert run["unit"]["serial_number"] == serial


def test_multiple_runs_for_same_serial(
    tofupilot_server_url, api_key, procedure_identifier
):
    """Create two runs for same serial → get_runs returns both."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"GR3-{uuid.uuid4().hex[:8]}"

    r1 = _create_run(client, serial, procedure_identifier, passed=True)
    r2 = _create_run(client, serial, procedure_identifier, passed=False)
    assert r1.get("id") and r2.get("id")

    result = client.get_runs(serial)
    assert result["success"] is True
    run_ids = [r["id"] for r in result["result"]]
    assert r1["id"] in run_ids
    assert r2["id"] in run_ids


def test_nonexistent_serial_returns_empty(
    tofupilot_server_url, api_key
):
    """get_runs("DOES-NOT-EXIST") → success with empty result list."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"GHOST-{uuid.uuid4().hex[:8]}"

    result = client.get_runs(serial)
    assert result["success"] is True
    assert result["result"] == []


def test_empty_serial_returns_client_error(
    tofupilot_server_url, api_key
):
    """get_runs("") → client-side error without API call."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)

    result = client.get_runs("")
    assert result["success"] is False
    assert "serial_number" in result["error"]["message"].lower()
