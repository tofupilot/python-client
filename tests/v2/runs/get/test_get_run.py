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

    def test_get_run_includes_mdm_data_series(
        self, client: TofuPilot, procedure_id: str
    ) -> None:
        """Test that get run returns multi-dimensional measurement data via data_series."""
        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]

        x_data = [0.0, 1.0, 2.0, 3.0, 4.0]
        y_voltage = [3.0, 3.2, 3.3, 3.2, 3.1]
        y_current = [0.5, 0.6, 0.7, 0.6, 0.5]

        create_result = client.runs.create(
            serial_number=f"SN-GET-MDM-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-GET-MDM-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
            phases=[
                {
                    "name": "MDM Phase",
                    "outcome": "PASS",
                    "started_at": started_at,
                    "ended_at": ended_at,
                    "measurements": [
                        {
                            "name": "voltage_vs_time",
                            "outcome": "PASS",
                            "x_axis": {
                                "data": x_data,
                                "units": "s",
                            },
                            "y_axis": [
                                {
                                    "data": y_voltage,
                                    "units": "V",
                                },
                                {
                                    "data": y_current,
                                    "units": "A",
                                },
                            ],
                        }
                    ],
                }
            ],
        )
        assert_create_run_success(create_result)

        result = client.runs.get(id=create_result.id)
        assert_get_run_success(result)

        # Verify phase and measurement exist
        assert result.phases is not None
        assert len(result.phases) >= 1
        phase = result.phases[0]
        assert phase.name == "MDM Phase"

        assert phase.measurements is not None
        assert len(phase.measurements) >= 1
        measurement = phase.measurements[0]
        assert measurement.name == "voltage_vs_time"
        assert measurement.outcome == "PASS"

        # Verify data_series contains all axes (x + 2 y-series = 3 series)
        assert measurement.data_series is not None
        assert len(measurement.data_series) == 3

        # Verify data values roundtrip correctly
        returned_data = [series.data for series in measurement.data_series]
        assert x_data in returned_data
        assert y_voltage in returned_data
        assert y_current in returned_data

        # Verify units roundtrip correctly
        returned_units = [series.units for series in measurement.data_series]
        assert "s" in returned_units
        assert "V" in returned_units
        assert "A" in returned_units

    def test_get_run_includes_mdm_with_validators_and_aggregations(
        self, client: TofuPilot, procedure_id: str
    ) -> None:
        """Test that get run returns MDM validators and aggregations via data_series."""
        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]

        create_result = client.runs.create(
            serial_number=f"SN-GET-MDM-VA-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-GET-MDM-VA-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
            phases=[
                {
                    "name": "MDM Validated Phase",
                    "outcome": "PASS",
                    "started_at": started_at,
                    "ended_at": ended_at,
                    "measurements": [
                        {
                            "name": "temperature_sweep",
                            "outcome": "PASS",
                            "x_axis": {
                                "data": [0.0, 1.0, 2.0],
                                "units": "s",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 0.0,
                                        "outcome": "PASS",
                                    }
                                ],
                                "aggregations": [
                                    {
                                        "type": "max",
                                        "outcome": "PASS",
                                        "value": 2.0,
                                        "unit": "s",
                                    }
                                ],
                            },
                            "y_axis": [
                                {
                                    "data": [25.0, 27.5, 26.0],
                                    "units": "C",
                                    "validators": [
                                        {
                                            "operator": "range",
                                            "expected_value": [20.0, 30.0],
                                            "outcome": "PASS",
                                        }
                                    ],
                                    "aggregations": [
                                        {
                                            "type": "avg",
                                            "outcome": "PASS",
                                            "value": 26.17,
                                            "unit": "C",
                                        }
                                    ],
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
        measurement = result.phases[0].measurements[0]
        assert measurement.name == "temperature_sweep"
        assert measurement.data_series is not None
        assert len(measurement.data_series) == 2

        # Verify at least one series has validators
        series_with_validators = [
            s for s in measurement.data_series if s.validators
        ]
        assert len(series_with_validators) >= 1

        # Verify at least one series has aggregations
        series_with_aggregations = [
            s for s in measurement.data_series if s.aggregations
        ]
        assert len(series_with_aggregations) >= 1

        # Verify validator details roundtrip
        for series in series_with_validators:
            validator = series.validators[0]
            assert validator.outcome in ("PASS", "FAIL", "UNSET")
            assert validator.expression is not None

        # Verify aggregation details roundtrip
        for series in series_with_aggregations:
            agg = series.aggregations[0]
            assert agg.type is not None
            assert agg.outcome in ("PASS", "FAIL", "UNSET", None)
            assert agg.value is not None
