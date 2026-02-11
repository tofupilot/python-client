"""Test validation rules for run creation."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.client_with_error_tracking import TofuPilotValidationError
from tofupilot.v2.errors import ErrorBADREQUEST, ErrorNOTFOUND
from ...utils import get_random_test_dates


def test_create_run_with_empty_serial_number(client: TofuPilot, procedure_id: str):
    """Test that creating a run with empty serial number fails."""
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(ErrorBADREQUEST) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="",
            procedure_id=procedure_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
    assert exc_info.value.data.issues and "serial number" in exc_info.value.data.issues[0].message.lower()


def test_create_run_with_whitespace_serial_number(client: TofuPilot, procedure_id: str):
    """Test that creating a run with whitespace-only serial number fails."""
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(ErrorBADREQUEST) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="   ",
            procedure_id=procedure_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
    assert exc_info.value.data.issues and "serial number" in exc_info.value.data.issues[0].message.lower()


def test_create_run_with_invalid_procedure_id(client: TofuPilot, auth_type):
    """Test that creating a run with non-existent procedure ID fails."""
    from tofupilot.v2.errors import ErrorFORBIDDEN

    fake_id = str(uuid.uuid4())
    started_at, ended_at = get_random_test_dates()

    if auth_type == "station":
        # Stations get a business-logic 403 (not linked to procedure), not an access-control 403
        with pytest.raises(ErrorFORBIDDEN) as exc_info:
            client.runs.create(  # type: ignore[call-arg]
                serial_number="TEST-001",
                procedure_id=fake_id,
                part_number="TEST-PCB-001",
                started_at=started_at,
                outcome="PASS",
                ended_at=ended_at,
            )
        assert "not authorized" in str(exc_info.value).lower()
        return

    with pytest.raises(ErrorNOTFOUND) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id=fake_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
    assert "procedure" in str(exc_info.value).lower()


def test_create_run_with_malformed_procedure_id(client: TofuPilot):
    """Test that creating a run with malformed procedure ID fails."""
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(ErrorBADREQUEST) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id="not-a-uuid",
            part_number="TEST-PCB-001",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
    assert exc_info.value.data.issues and "uuid" in exc_info.value.data.issues[0].message.lower()


def test_create_run_with_invalid_outcome(client: TofuPilot, procedure_id: str):
    """Test that creating a run with invalid outcome value fails."""
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(TofuPilotValidationError) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id=procedure_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            outcome="INVALID_OUTCOME",  # type: ignore[arg-type]
            ended_at=ended_at,
        )
    assert "outcome" in str(exc_info.value).lower()


def test_create_run_with_end_before_start(client: TofuPilot, procedure_id: str):
    """Test that creating a run with end time before start time succeeds (validation not enforced)."""
    start_time = datetime.now(timezone.utc)
    end_time = start_time - timedelta(hours=1)
    
    # This should succeed as the API doesn't enforce time order validation
    result = client.runs.create(
        serial_number="TEST-001",
        procedure_id=procedure_id,
        part_number="TEST-PCB-001",
        started_at=start_time,
        ended_at=end_time,
        outcome="PASS",
    )
    assert result.id is not None


def test_create_run_with_ended_at_but_no_outcome(client: TofuPilot, procedure_id: str):
    """Test that providing ended_at without outcome fails at Python SDK level."""
    started_at, ended_at = get_random_test_dates(duration_minutes=10)
    with pytest.raises(TypeError) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id=procedure_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            ended_at=ended_at,
        )
    assert "outcome" in str(exc_info.value)


def test_create_run_with_outcome_but_no_ended_at(client: TofuPilot, procedure_id: str):
    """Test that providing outcome without ended_at fails at Python SDK level."""
    started_at, _ = get_random_test_dates()
    with pytest.raises(TypeError) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id=procedure_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            outcome="PASS",
        )
    assert "ended_at" in str(exc_info.value)


def test_create_run_with_very_long_serial_number(client: TofuPilot, procedure_id: str):
    """Test that creating a run with very long serial number fails."""
    long_serial = "A" * 1001  # Assuming 1000 char limit
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(ErrorBADREQUEST) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number=long_serial,
            procedure_id=procedure_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
    assert exc_info.value.data.issues and ("serial number" in exc_info.value.data.issues[0].message.lower() or "length" in exc_info.value.data.issues[0].message.lower())


def test_create_run_with_invalid_batch_number(client: TofuPilot, procedure_id: str):
    """Test that creating a run with empty batch number fails."""
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(ErrorBADREQUEST) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id=procedure_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            batch_number="",  # Empty batch number should fail
            outcome="PASS",
            ended_at=ended_at,
        )
    assert exc_info.value.data.issues and "batch" in exc_info.value.data.issues[0].message.lower()


def test_create_run_with_invalid_part_number(client: TofuPilot, procedure_id: str):
    """Test that creating a run with malformed part number fails."""
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(ErrorBADREQUEST) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id=procedure_id,
            started_at=started_at,
            part_number="",  # Empty part number should fail
            outcome="PASS",
            ended_at=ended_at,
        )
    assert exc_info.value.data.issues and "part" in exc_info.value.data.issues[0].message.lower()


def test_create_run_with_invalid_operated_by(client: TofuPilot, procedure_id: str):
    """Test that creating a run with invalid operated_by fails."""
    # Test with empty list
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(ErrorBADREQUEST) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id=procedure_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            operated_by="invalid_operator",
            outcome="PASS",
            ended_at=ended_at,
        )
    assert exc_info.value.data.issues and ("operated_by" in exc_info.value.data.issues[0].message.lower() or "email" in exc_info.value.data.issues[0].message.lower())

    # Test with empty string in list
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(ErrorBADREQUEST) as exc_info:
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id=procedure_id,
            part_number="TEST-PCB-001",
            started_at=started_at,
            operated_by="",
            outcome="PASS",
            ended_at=ended_at,
        )
    assert exc_info.value.data.issues and ("operated_by" in exc_info.value.data.issues[0].message.lower() or "email" in exc_info.value.data.issues[0].message.lower())


def test_create_run_with_procedure_version(client: TofuPilot, procedure_id: str):
    """Test that creating a run with procedure_version links the run to a version."""
    started_at, ended_at = get_random_test_dates()
    version_tag = f"v{uuid.uuid4().hex[:8]}"

    result = client.runs.create(
        serial_number="TEST-001",
        procedure_id=procedure_id,
        part_number="TEST-PCB-001",
        started_at=started_at,
        ended_at=ended_at,
        outcome="PASS",
        procedure_version=version_tag,
    )
    assert result.id is not None

    # Verify via get that the version was stored
    run = client.runs.get(id=result.id)
    assert run.procedure.version is not None
    assert run.procedure.version.tag.lower() == version_tag.lower()


def test_create_run_with_docstring(client: TofuPilot, procedure_id: str):
    """Test that creating a run with docstring stores the documentation."""
    started_at, ended_at = get_random_test_dates()
    doc = "Automated regression test for power supply module."

    result = client.runs.create(
        serial_number="TEST-001",
        procedure_id=procedure_id,
        part_number="TEST-PCB-001",
        started_at=started_at,
        ended_at=ended_at,
        outcome="PASS",
        docstring=doc,
    )
    assert result.id is not None

    # Verify via get that the docstring was stored
    run = client.runs.get(id=result.id)
    assert run.docstring == doc


def test_create_run_without_required_fields(client: TofuPilot):
    """Test that creating a run without required fields fails."""
    # Missing serial_number - Python SDK enforces this at function level
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(TypeError):
        client.runs.create(  # type: ignore[call-arg]
            procedure_id=str(uuid.uuid4()),
            part_number="TEST-PCB-001",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )

    # Missing procedure_id - Python SDK enforces this at function level
    started_at, ended_at = get_random_test_dates()
    with pytest.raises(TypeError):
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            part_number="TEST-PCB-001",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )

    # Missing started_at - Python SDK enforces this at function level
    with pytest.raises(TypeError):
        client.runs.create(  # type: ignore[call-arg]
            serial_number="TEST-001",
            procedure_id=str(uuid.uuid4()),
            part_number="TEST-PCB-001",
            outcome="PASS",
            ended_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )