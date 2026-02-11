"""Tests for TofuPilotClient error handling — Section 11."""

import uuid

import pytest
from tofupilot import TofuPilotClient


def test_invalid_api_key(tofupilot_server_url, procedure_identifier):
    """Invalid API key → authentication error with success=False."""
    client = TofuPilotClient(api_key="invalid-key-000", url=tofupilot_server_url)

    result = client.create_run(
        unit_under_test={"serial_number": f"ERR1-{uuid.uuid4().hex[:8]}", "part_number": "test_err"},
        run_passed=True,
        procedure_id=procedure_identifier,
    )

    assert result["success"] is False
    assert result.get("status_code") in (401, 403)


def test_missing_serial_number(tofupilot_server_url, api_key, procedure_identifier):
    """Missing serial_number in unit_under_test → server rejects with 400."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)

    result = client.create_run(
        unit_under_test={"part_number": "test_err_no_sn"},
        run_passed=True,
        procedure_id=procedure_identifier,
    )

    assert result["success"] is False
    assert result.get("status_code") == 400


def test_network_timeout(api_key):
    """Unreachable server → network error with success=False."""
    client = TofuPilotClient(api_key=api_key, url="http://localhost:1")

    result = client.create_run(
        unit_under_test={"serial_number": f"ERR3-{uuid.uuid4().hex[:8]}", "part_number": "test_err"},
        run_passed=True,
        procedure_id="does-not-matter",
    )

    assert result["success"] is False
    assert "error" in result


def test_invalid_file_path(tofupilot_server_url, api_key, procedure_identifier):
    """Nonexistent file path → FileNotFoundError before upload."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)

    with pytest.raises(FileNotFoundError):
        client.create_run(
            unit_under_test={"serial_number": f"ERR4-{uuid.uuid4().hex[:8]}", "part_number": "test_err"},
            run_passed=True,
            procedure_id=procedure_identifier,
            attachments=["/nonexistent/path/to/file.txt"],
        )
