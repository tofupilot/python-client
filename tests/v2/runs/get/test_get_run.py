"""Test getting individual run details."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ...utils import (
    assert_create_run_success,
    assert_get_run_success,
    get_random_test_dates,
)


class TestGetRun:
    """Test getting individual run details."""

    def test_get_run_by_id(self, client: TofuPilot, procedure_id: str) -> None:
        """Test getting a run by its ID and verifying top-level fields."""
        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]

        create_result = client.runs.create(
            serial_number=f"SN-GET-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-GET-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        result = client.runs.get(id=create_result.id)
        assert_get_run_success(result)

        assert result.id == create_result.id
        assert result.outcome == "PASS"
        assert result.started_at is not None
        assert result.ended_at is not None
        assert result.duration is not None
        assert result.procedure is not None
        assert result.procedure.id == procedure_id
        assert result.unit is not None
        assert result.unit.serial_number == f"SN-GET-{unique_id}"

    def test_get_nonexistent_run(self, client: TofuPilot) -> None:
        """Test getting a run that doesn't exist."""
        nonexistent_id = str(uuid.uuid4())

        with pytest.raises(ErrorNOTFOUND):
            client.runs.get(id=nonexistent_id)

    def test_get_run_includes_phases_and_measurements(
        self, client: TofuPilot, procedure_id: str
    ) -> None:
        """Test that get run includes phases and measurements in nested structure."""
        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]

        create_result = client.runs.create(
            serial_number=f"SN-GET-PHASES-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-GET-PHASES-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
            phases=[
                {
                    "name": "Voltage Test",
                    "outcome": "PASS",
                    "started_at": started_at,
                    "ended_at": ended_at,
                    "measurements": [
                        {
                            "name": "voltage",
                            "outcome": "PASS",
                            "measured_value": 3.3,
                            "units": "V",
                            "validators": [
                                {
                                    "operator": ">=",
                                    "expected_value": 3.0,
                                    "outcome": "PASS",
                                }
                            ],
                        }
                    ],
                }
            ],
        )
        assert_create_run_success(create_result)

        result = client.runs.get(id=create_result.id)
        assert_get_run_success(result)

        assert result.phases is not None
        assert len(result.phases) >= 1
        phase = result.phases[0]
        assert phase.name == "Voltage Test"
        assert phase.outcome == "PASS"

        assert phase.measurements is not None
        assert len(phase.measurements) >= 1
        measurement = phase.measurements[0]
        assert measurement.name == "voltage"
        assert measurement.outcome == "PASS"
        assert measurement.measured_value == 3.3

    def test_get_run_includes_logs(
        self, client: TofuPilot, procedure_id: str
    ) -> None:
        """Test that get run includes logs with correct level and message."""
        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]

        create_result = client.runs.create(
            serial_number=f"SN-GET-LOGS-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-GET-LOGS-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
            logs=[
                {
                    "level": "INFO",
                    "timestamp": started_at,
                    "message": "Test started",
                    "source_file": "test_get_run.py",
                    "line_number": 1,
                },
                {
                    "level": "WARNING",
                    "timestamp": ended_at,
                    "message": "Voltage near threshold",
                    "source_file": "test_get_run.py",
                    "line_number": 2,
                },
            ],
        )
        assert_create_run_success(create_result)

        result = client.runs.get(id=create_result.id)
        assert_get_run_success(result)

        assert result.logs is not None
        assert len(result.logs) >= 2

        log_messages = {log.message for log in result.logs}
        assert "Test started" in log_messages
        assert "Voltage near threshold" in log_messages

    def test_get_run_includes_sub_units(
        self, client: TofuPilot, procedure_id: str
    ) -> None:
        """Test that get run includes sub_units in response."""
        unique_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc)

        # Create sub-unit run first
        sub_serial = f"SubUnit-Get-{unique_id}"
        sub_result = client.runs.create(
            serial_number=sub_serial,
            procedure_id=procedure_id,
            part_number=f"SubPart-Get-{unique_id}",
            started_at=now - timedelta(minutes=10),
            outcome="PASS",
            ended_at=now - timedelta(minutes=8),
        )
        assert_create_run_success(sub_result)

        # Create main run with sub-unit
        main_result = client.runs.create(
            serial_number=f"MainUnit-Get-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"MainPart-Get-{unique_id}",
            started_at=now - timedelta(minutes=5),
            outcome="PASS",
            ended_at=now,
            sub_units=[sub_serial],
        )
        assert_create_run_success(main_result)

        result = client.runs.get(id=main_result.id)
        assert_get_run_success(result)

        assert result.sub_units is not None
        assert len(result.sub_units) >= 1
        sub_serials = [su.serial_number for su in result.sub_units]
        assert sub_serial in sub_serials
