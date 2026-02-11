"""Tests for OpenHTF-specific features (Section 8 of README).

Covers:
- sub_units via htf.Test()
- allow_nan in OpenHTF JSON serialization
- PhaseOptions timeout outcome
- PhaseResult.STOP halting execution
"""

import time
import uuid
from datetime import datetime, timedelta, timezone

import openhtf as htf
from openhtf import PhaseResult
from tofupilot.openhtf import TofuPilot, upload
import tofupilot


# --- Phase definitions ---


@htf.measures(
    htf.Measurement("nan_value"),
    htf.Measurement("normal_value"),
)
def phase_with_nan_measurement(test):
    test.measurements.nan_value = float("nan")
    test.measurements.normal_value = 42.0


@htf.PhaseOptions(timeout_s=1)
@htf.measures(htf.Measurement("timed_out_value"))
def phase_that_times_out(test):
    time.sleep(10)
    test.measurements.timed_out_value = 1


def phase_after_timeout(test):
    return PhaseResult.CONTINUE


def phase_before_stop(test):
    return PhaseResult.CONTINUE


def phase_that_stops(test):
    return PhaseResult.STOP


@htf.measures(htf.Measurement("unreachable").equals(True))
def phase_after_stop(test):
    test.measurements.unreachable = True


def simple_passing_phase(test):
    return PhaseResult.CONTINUE


# --- Tests ---


def test_allow_nan_in_openhtf_json(
    tofupilot_server_url, api_key, procedure_identifier
):
    """NaN measurement values can be uploaded with allow_nan=True."""
    test = htf.Test(
        phase_with_nan_measurement,
        procedure_id=procedure_identifier,
        part_number="test_nan",
    )
    test.add_output_callbacks(
        upload(api_key=api_key, url=tofupilot_server_url, allow_nan=True)
    )
    test.execute(lambda: f"NAN-{uuid.uuid4().hex[:8]}")


def test_phase_timeout_outcome(
    tofupilot_server_url,
    api_key,
    procedure_identifier,
    procedure_id,
    extract_id_and_check_run_exists,
):
    """PhaseOptions timeout_s triggers non-PASS outcome on the timed-out phase."""
    serial = f"TIMEOUT-{uuid.uuid4().hex[:8]}"

    test = htf.Test(
        phase_that_times_out,
        phase_after_timeout,
        procedure_id=procedure_identifier,
        part_number="test_timeout",
    )

    with TofuPilot(test, url=tofupilot_server_url, api_key=api_key, stream=False):
        test.execute(lambda: serial)

    run = extract_id_and_check_run_exists(
        serial_number=serial,
        procedure_id=procedure_id,
        part_number="test_timeout",
    )

    phase_names = [p.name for p in run.phases]
    assert "phase_that_times_out" in phase_names

    timeout_phase = run.phases[phase_names.index("phase_that_times_out")]
    assert timeout_phase.outcome != "PASS", (
        f"Expected non-PASS outcome for timed-out phase, got {timeout_phase.outcome}"
    )


def test_phase_result_stop_halts_execution(
    tofupilot_server_url,
    api_key,
    procedure_identifier,
    procedure_id,
    extract_id_and_check_run_exists,
):
    """PhaseResult.STOP prevents subsequent phases from executing."""
    serial = f"STOP-{uuid.uuid4().hex[:8]}"

    test = htf.Test(
        phase_before_stop,
        phase_that_stops,
        phase_after_stop,
        procedure_id=procedure_identifier,
        part_number="test_stop",
    )

    with TofuPilot(test, url=tofupilot_server_url, api_key=api_key, stream=False):
        test.execute(lambda: serial)

    run = extract_id_and_check_run_exists(
        serial_number=serial,
        procedure_id=procedure_id,
        part_number="test_stop",
    )

    phase_names = [p.name for p in run.phases]

    assert "phase_before_stop" in phase_names
    assert "phase_that_stops" in phase_names

    # Phase after STOP should not have been executed
    assert "phase_after_stop" not in phase_names, (
        "phase_after_stop should not appear after PhaseResult.STOP"
    )


def test_sub_units_via_openhtf(
    tofupilot_server_url,
    api_key,
    procedure_identifier,
    procedure_id,
    extract_id_and_check_run_exists,
):
    """sub_units parameter on htf.Test() links sub-units to the main unit."""
    unique_id = uuid.uuid4().hex[:8]
    sub_serial = f"SUB-{unique_id}"
    main_serial = f"MAIN-{unique_id}"

    # Create sub-unit via V2 client so it exists before the OpenHTF run
    v2_client = tofupilot.v2.TofuPilot(
        api_key=api_key,
        server_url=f"{tofupilot_server_url}/api",
    )
    now = datetime.now(timezone.utc)
    v2_client.runs.create(
        serial_number=sub_serial,
        procedure_id=procedure_id,
        outcome="PASS",
        part_number="test_sub_unit",
        started_at=now - timedelta(minutes=5),
        ended_at=now,
    )

    # Create main unit via OpenHTF with sub_units metadata
    main_test = htf.Test(
        simple_passing_phase,
        procedure_id=procedure_identifier,
        part_number="test_main_unit",
        sub_units=[{"serial_number": sub_serial}],
    )
    with TofuPilot(
        main_test, url=tofupilot_server_url, api_key=api_key, stream=False
    ):
        main_test.execute(lambda: main_serial)

    run = extract_id_and_check_run_exists(
        serial_number=main_serial,
        procedure_id=procedure_id,
        part_number="test_main_unit",
    )
    assert run.id
