"""Tests for TofuPilotClient.create_run() — Section 9c: Phases and Measurements."""

import uuid
from datetime import datetime, timezone

from tofupilot import TofuPilotClient, PhaseOutcome, MeasurementOutcome


def _now_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def test_phases_with_mixed_outcomes(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """Multiple phases with PASS and FAIL outcomes → each outcome preserved on created run."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"PHASE-{uuid.uuid4().hex[:8]}"
    t = _now_ms()

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_phases"},
        run_passed=False,
        procedure_id=procedure_identifier,
        phases=[
            {"name": "power_check", "outcome": PhaseOutcome.PASS,
             "start_time_millis": t, "end_time_millis": t + 1000},
            {"name": "voltage_check", "outcome": PhaseOutcome.FAIL,
             "start_time_millis": t + 1000, "end_time_millis": t + 2000},
            {"name": "cleanup", "outcome": PhaseOutcome.PASS,
             "start_time_millis": t + 2000, "end_time_millis": t + 3000},
        ],
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(result["id"], serial_number=serial, procedure_id=procedure_id)

    phases_by_name = {p.name: p for p in run.phases}
    assert "power_check" in phases_by_name
    assert "voltage_check" in phases_by_name
    assert "cleanup" in phases_by_name
    assert phases_by_name["power_check"].outcome == "PASS"
    assert phases_by_name["voltage_check"].outcome == "FAIL"
    assert phases_by_name["cleanup"].outcome == "PASS"


def test_measurement_with_limits(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """Measurement limits (lower_limit, upper_limit) roundtrip; value and validators verified."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"LIM-{uuid.uuid4().hex[:8]}"
    t = _now_ms()

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_limits"},
        run_passed=True,
        procedure_id=procedure_identifier,
        phases=[{
            "name": "voltage_test",
            "outcome": PhaseOutcome.PASS,
            "start_time_millis": t,
            "end_time_millis": t + 1000,
            "measurements": [{
                "name": "input_voltage",
                "outcome": MeasurementOutcome.PASS,
                "measured_value": 4.8,
                "units": "V",
                "lower_limit": 4.5,
                "upper_limit": 5.0,
            }],
        }],
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(result["id"], serial_number=serial, procedure_id=procedure_id)

    phase = next(p for p in run.phases if p.name == "voltage_test")
    m = next(m for m in phase.measurements if m.name == "input_voltage")
    assert m.measured_value == 4.8
    assert m.units == "V"
    assert m.validators, "Expected validators from limits"


def test_measurement_units_preserved(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """units field on Measurement dict roundtrips (V, A, %)."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"UNIT-{uuid.uuid4().hex[:8]}"
    t = _now_ms()

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_units"},
        run_passed=True,
        procedure_id=procedure_identifier,
        phases=[{
            "name": "electrical_test",
            "outcome": PhaseOutcome.PASS,
            "start_time_millis": t,
            "end_time_millis": t + 1000,
            "measurements": [
                {"name": "voltage", "outcome": MeasurementOutcome.PASS, "measured_value": 3.3, "units": "V"},
                {"name": "current", "outcome": MeasurementOutcome.PASS, "measured_value": 0.5, "units": "A"},
                {"name": "efficiency", "outcome": MeasurementOutcome.PASS, "measured_value": 92.0, "units": "%"},
            ],
        }],
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(result["id"], serial_number=serial, procedure_id=procedure_id)

    phase = next(p for p in run.phases if p.name == "electrical_test")
    by_name = {m.name: m for m in phase.measurements}
    assert by_name["voltage"].units == "V"
    assert by_name["current"].units == "A"
    assert by_name["efficiency"].units == "%"


def test_measurement_outcomes_preserved(
    tofupilot_server_url, api_key, procedure_identifier, procedure_id, check_run_exists
):
    """Each MeasurementOutcome (PASS, FAIL, UNSET) stored and retrievable."""
    client = TofuPilotClient(api_key=api_key, url=tofupilot_server_url)
    serial = f"MOUT-{uuid.uuid4().hex[:8]}"
    t = _now_ms()

    result = client.create_run(
        unit_under_test={"serial_number": serial, "part_number": "test_cr_mout"},
        run_passed=False,
        procedure_id=procedure_identifier,
        phases=[{
            "name": "outcome_test",
            "outcome": PhaseOutcome.FAIL,
            "start_time_millis": t,
            "end_time_millis": t + 1000,
            "measurements": [
                {"name": "passing", "outcome": MeasurementOutcome.PASS, "measured_value": 1.0},
                {"name": "failing", "outcome": MeasurementOutcome.FAIL, "measured_value": 99.0},
                {"name": "unset_m", "outcome": MeasurementOutcome.UNSET},
            ],
        }],
    )

    assert result.get("id"), f"Expected run ID in response, got: {result}"
    run = check_run_exists(result["id"], serial_number=serial, procedure_id=procedure_id)

    phase = next(p for p in run.phases if p.name == "outcome_test")
    by_name = {m.name: m for m in phase.measurements}
    assert by_name["passing"].outcome == "PASS"
    assert by_name["failing"].outcome == "FAIL"
    assert by_name["unset_m"].outcome == "UNSET"
