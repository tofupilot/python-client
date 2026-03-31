"""Tests for TofuPilotClient.create_run() — Section 9d: Attachments (direct file paths)."""

import uuid

import pytest
from tofupilot import TofuPilotClient


def test_single_file_attachment(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """File path in attachments list → attachment name appears on created run."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"ATT1-{uuid.uuid4().hex[:8]}"

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_att1"},
        run_passed=True,
        procedure_id=procedure_identifier,
        attachments=["tests/v1/attachments/oscilloscope.jpeg"],
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(result["id"], serial_number=serial, procedure_id=procedure_id)
    attachment_names = [a.name for a in run.attachments]
    assert "oscilloscope.jpeg" in attachment_names


def test_multiple_file_attachments(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """Multiple file paths → all attachment names present on created run."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"ATTM-{uuid.uuid4().hex[:8]}"

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_attm"},
        run_passed=True,
        procedure_id=procedure_identifier,
        attachments=[
            "tests/v1/attachments/oscilloscope.jpeg",
            "tests/v1/attachments/sample_file.txt",
        ],
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(result["id"], serial_number=serial, procedure_id=procedure_id)
    attachment_names = [a.name for a in run.attachments]
    assert "oscilloscope.jpeg" in attachment_names
    assert "sample_file.txt" in attachment_names


def test_oversized_file_rejected(
    tofupilot_server_url, api_key, procedure_identifier, tmp_path
):
    """File >10MB rejected by validate_files() before upload."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    big_file = tmp_path / "oversized.bin"
    big_file.write_bytes(b"\x00" * (11 * 1024 * 1024))

    with pytest.raises(SystemExit):
        client.create_run(
            unit_under_test={"serial_number": "OVER-001", "part_number": "test_cr_over"},
            run_passed=True,
            procedure_id=procedure_identifier,
            attachments=[str(big_file)],
        )


def test_too_many_attachments_rejected(
    tofupilot_server_url, api_key, procedure_identifier, tmp_path
):
    """>100 attachments rejected by validate_files() before upload."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)

    files = []
    for i in range(101):
        f = tmp_path / f"file_{i}.txt"
        f.write_text(f"content {i}")
        files.append(str(f))

    with pytest.raises(SystemExit):
        client.create_run(
            unit_under_test={"serial_number": "MANY-001", "part_number": "test_cr_many"},
            run_passed=True,
            procedure_id=procedure_identifier,
            attachments=files,
        )
