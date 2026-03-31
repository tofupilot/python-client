"""Tests for TofuPilotClient.create_run() — Section 9e: Logs (direct)."""

import uuid

from tofupilot import TofuPilotClient
from tofupilot.v1.models.models import LogLevel


def test_log_levels_preserved(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """Log entries with DEBUG through CRITICAL → each level and message verified on created run."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"LOG-{uuid.uuid4().hex[:8]}"
    ts = "2025-06-15T12:00:00Z"

    logs = [
        {"level": LogLevel.DEBUG, "timestamp": ts, "message": "debug msg", "source_file": "test.py", "line_number": 10},
        {"level": LogLevel.INFO, "timestamp": ts, "message": "info msg", "source_file": "test.py", "line_number": 20},
        {"level": LogLevel.WARNING, "timestamp": ts, "message": "warning msg", "source_file": "test.py", "line_number": 30},
        {"level": LogLevel.ERROR, "timestamp": ts, "message": "error msg", "source_file": "test.py", "line_number": 40},
        {"level": LogLevel.CRITICAL, "timestamp": ts, "message": "critical msg", "source_file": "test.py", "line_number": 50},
    ]

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_logs"},
        run_passed=True,
        procedure_id=procedure_identifier,
        logs=logs,
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(result["id"], serial_number=serial, procedure_id=procedure_id)

    assert run.logs, "Expected logs on created run"
    by_message = {log.message: log for log in run.logs}
    for entry in logs:
        msg = entry["message"]
        assert msg in by_message, f"Log '{msg}' not found on run"
        assert by_message[msg].level == entry["level"].value


def test_log_source_metadata_preserved(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """timestamp, source_file, line_number roundtrip on created run."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"LMETA-{uuid.uuid4().hex[:8]}"
    ts = "2025-06-15T14:30:00Z"

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_lmeta"},
        run_passed=True,
        procedure_id=procedure_identifier,
        logs=[{
            "level": LogLevel.INFO,
            "timestamp": ts,
            "message": "metadata check",
            "source_file": "sensor_driver.py",
            "line_number": 42,
        }],
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(result["id"], serial_number=serial, procedure_id=procedure_id)

    log = next(l for l in run.logs if l.message == "metadata check")
    assert log.source_file == "sensor_driver.py"
    assert log.line_number == 42
    assert log.timestamp is not None
