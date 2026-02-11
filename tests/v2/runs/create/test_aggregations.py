"""Test aggregation syntax for run creation.

This test suite covers aggregations computed over measurement values (min, max, avg, etc.)
with optional validators on aggregated values.
"""

import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError
from ...utils import get_random_test_dates, assert_create_run_success


# =============================================================================
# BASIC AGGREGATION TYPES
# =============================================================================


def test_aggregation_avg(client: TofuPilot, procedure_id: str):
    """Test aggregation with type 'avg' (average)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-AVG-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-001",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Average Aggregation Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_readings",
                        "outcome": "PASS",
                        "measured_value": [3.2, 3.3, 3.4, 3.3, 3.2],
                        "units": "V",
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": 3.28,
                                "outcome": "PASS",
                                "unit": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)
    assert result.id is not None


def test_aggregation_type_with_special_characters(client: TofuPilot, procedure_id: str):
    """Test aggregation with special characters in type (%, -, /, _)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-SPECIAL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-SPECIAL",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Special Character Types",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "custom_stats",
                        "outcome": "PASS",
                        "measured_value": [1.0, 2.0, 3.0, 4.0, 5.0],
                        "aggregations": [
                            {"type": "%max", "value": 100, "outcome": "PASS"},
                            {"type": "max-min", "value": 4.0, "outcome": "PASS"},
                            {"type": "max/range", "value": 1.25, "outcome": "PASS"},
                            {"type": "percentile_95", "value": 4.8, "outcome": "PASS"},
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# MULTIPLE AGGREGATIONS
# =============================================================================


def test_multiple_aggregations_on_single_measurement(client: TofuPilot, procedure_id: str):
    """Test multiple aggregations on a single measurement."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MULTI-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-009",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Multiple Aggregations Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_stats",
                        "outcome": "PASS",
                        "measured_value": [3.0, 3.1, 3.2, 3.3, 3.4, 3.5],
                        "units": "V",
                        "aggregations": [
                            {
                                "type": "min",
                                "value": 3.0,
                                "outcome": "PASS",
                                "unit": "V"
                            },
                            {
                                "type": "max",
                                "value": 3.5,
                                "outcome": "PASS",
                                "unit": "V"
                            },
                            {
                                "type": "avg",
                                "value": 3.25,
                                "outcome": "PASS",
                                "unit": "V"
                            },
                            {
                                "type": "std",
                                "value": 0.18,
                                "outcome": "PASS",
                                "unit": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# AGGREGATION OUTCOMES
# =============================================================================


def test_aggregation_outcome_pass(client: TofuPilot, procedure_id: str):
    """Test aggregation with PASS outcome."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-PASS-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-010",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Pass Outcome Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "test_data",
                        "outcome": "PASS",
                        "measured_value": [100, 105, 102, 98, 103],
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": 101.6,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_aggregation_outcome_fail(client: TofuPilot, procedure_id: str):
    """Test aggregation with FAIL outcome."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-FAIL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-011",
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "Fail Outcome Test",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "out_of_spec_data",
                        "outcome": "FAIL",
                        "measured_value": [150, 160, 155, 158, 162],
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": 157,
                                "outcome": "FAIL"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_aggregation_outcome_unset(client: TofuPilot, procedure_id: str):
    """Test aggregation with UNSET outcome (no validation)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-UNSET-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-012",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Unset Outcome Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "unvalidated_data",
                        "outcome": "UNSET",
                        "measured_value": [50, 55, 60, 65, 70],
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": 60,
                                "outcome": "UNSET"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# AGGREGATIONS WITH VALIDATORS
# =============================================================================


def test_aggregation_with_single_validator(client: TofuPilot, procedure_id: str):
    """Test aggregation with a single validator on aggregated value."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-VAL-1-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-013",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Aggregation with Validator",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_avg",
                        "outcome": "PASS",
                        "measured_value": [3.2, 3.3, 3.4],
                        "units": "V",
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": 3.3,
                                "outcome": "PASS",
                                "unit": "V",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 3.0,
                                        "outcome": "PASS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_aggregation_with_multiple_validators(client: TofuPilot, procedure_id: str):
    """Test aggregation with multiple validators (range check)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-VAL-MULTI-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-014",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Aggregation with Multiple Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "max_voltage",
                        "outcome": "PASS",
                        "measured_value": [3.0, 3.2, 3.5, 3.3, 3.1],
                        "units": "V",
                        "aggregations": [
                            {
                                "type": "max",
                                "value": 3.5,
                                "outcome": "PASS",
                                "unit": "V",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 3.0,
                                        "outcome": "PASS"
                                    },
                                    {
                                        "operator": "<=",
                                        "expected_value": 3.6,
                                        "outcome": "PASS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_aggregation_with_failing_validator(client: TofuPilot, procedure_id: str):
    """Test aggregation where validator fails."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-VAL-FAIL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-015",
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "Aggregation Validator Failure",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "max_current",
                        "outcome": "FAIL",
                        "measured_value": [1.5, 1.8, 2.1, 1.9, 1.7],
                        "units": "A",
                        "aggregations": [
                            {
                                "type": "max",
                                "value": 2.1,
                                "outcome": "FAIL",
                                "unit": "A",
                                "validators": [
                                    {
                                        "operator": "<=",
                                        "expected_value": 2.0,
                                        "outcome": "FAIL",
                                        "is_decisive": True
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_aggregation_validator_with_is_decisive(client: TofuPilot, procedure_id: str):
    """Test aggregation validator with is_decisive flag."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-DFM-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-016",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Aggregation DFM Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "avg_with_warning",
                        "outcome": "PASS",
                        "measured_value": [98, 99, 100, 101, 102],
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": 100,
                                "outcome": "PASS",
                                "validators": [
                                    {
                                        "operator": "<=",
                                        "expected_value": 95,
                                        "outcome": "FAIL",
                                        "is_decisive": False  # Warning only
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_multiple_aggregations_each_with_validators(client: TofuPilot, procedure_id: str):
    """Test multiple aggregations each with their own validators."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-COMPLEX-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-017",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Complex Aggregations Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "comprehensive_stats",
                        "outcome": "PASS",
                        "measured_value": [3.0, 3.1, 3.2, 3.3, 3.4],
                        "units": "V",
                        "aggregations": [
                            {
                                "type": "min",
                                "value": 3.0,
                                "outcome": "PASS",
                                "unit": "V",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 2.8,
                                        "outcome": "PASS"
                                    }
                                ]
                            },
                            {
                                "type": "max",
                                "value": 3.4,
                                "outcome": "PASS",
                                "unit": "V",
                                "validators": [
                                    {
                                        "operator": "<=",
                                        "expected_value": 3.6,
                                        "outcome": "PASS"
                                    }
                                ]
                            },
                            {
                                "type": "avg",
                                "value": 3.2,
                                "outcome": "PASS",
                                "unit": "V",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 3.0,
                                        "outcome": "PASS"
                                    },
                                    {
                                        "operator": "<=",
                                        "expected_value": 3.4,
                                        "outcome": "PASS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# AGGREGATIONS WITH STRING AND BOOLEAN VALUES
# =============================================================================


def test_aggregation_with_string_value(client: TofuPilot, procedure_id: str):
    """Test aggregation with string value (e.g., mode of categorical data)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-STR-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-018",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "String Aggregation Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "status_mode",
                        "outcome": "PASS",
                        "measured_value": ["OK", "OK", "OK", "WARNING", "OK"],
                        "aggregations": [
                            {
                                "type": "mode",
                                "value": "OK",
                                "outcome": "PASS",
                                "validators": [
                                    {
                                        "operator": "==",
                                        "expected_value": "OK",
                                        "outcome": "PASS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_aggregation_with_boolean_value(client: TofuPilot, procedure_id: str):
    """Test aggregation with boolean value (e.g., all pass check)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-BOOL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-019",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Boolean Aggregation Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "all_connected",
                        "outcome": "PASS",
                        "measured_value": [True, True, True, True, True],
                        "aggregations": [
                            {
                                "type": "all",
                                "value": True,
                                "outcome": "PASS",
                                "validators": [
                                    {
                                        "operator": "==",
                                        "expected_value": True,
                                        "outcome": "PASS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# NULL/EMPTY AGGREGATIONS
# =============================================================================


def test_measurement_with_no_aggregations(client: TofuPilot, procedure_id: str):
    """Test measurement without aggregations (omitted field)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-NO-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-020",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "No Aggregation Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "no_aggregation",
                        "outcome": "PASS",
                        "measured_value": [1, 2, 3, 4, 5]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_measurement_with_empty_aggregations_array(client: TofuPilot, procedure_id: str):
    """Test measurement with empty aggregations array."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-EMPTY-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-021",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Empty Aggregations Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "empty_aggregations",
                        "outcome": "PASS",
                        "measured_value": [1, 2, 3],
                        "aggregations": []
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_measurement_with_null_aggregations(client: TofuPilot, procedure_id: str):
    """Test measurement with null aggregations field."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-NULL-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGGREGATION-022",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Null Aggregations Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "null_aggregations",
                        "outcome": "PASS",
                        "measured_value": [1, 2, 3],
                        "aggregations": None
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# STATION ACCESS CONTROL
# =============================================================================


def test_station_can_create_run_with_aggregations(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can create runs with aggregations."""
    if auth_type != "station":
        return

    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-STATION-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Station Aggregation Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_stats",
                        "outcome": "PASS",
                        "measured_value": [3.2, 3.3, 3.4, 3.3, 3.2],
                        "units": "V",
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": 3.28,
                                "outcome": "PASS",
                                "unit": "V"
                            },
                            {
                                "type": "min",
                                "value": 3.2,
                                "outcome": "PASS",
                                "unit": "V"
                            },
                            {
                                "type": "max",
                                "value": 3.4,
                                "outcome": "PASS",
                                "unit": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_station_can_create_run_with_aggregations_and_validators(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can create runs with aggregations that have validators."""
    if auth_type != "station":
        return

    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-STATION-AGG-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Station Agg with Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "validated_avg",
                        "outcome": "PASS",
                        "measured_value": [3.0, 3.1, 3.2, 3.3],
                        "units": "V",
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": 3.15,
                                "outcome": "PASS",
                                "unit": "V",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 3.0,
                                        "outcome": "PASS"
                                    },
                                    {
                                        "operator": "<=",
                                        "expected_value": 3.5,
                                        "outcome": "PASS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# EDGE CASES - AGGREGATION VALIDATOR TYPE MISMATCHES
# =============================================================================


def test_aggregation_validator_type_mismatch(client: TofuPilot, procedure_id: str):
    """Test aggregation with validator that has type mismatch."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-TYPE-MISMATCH-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGG-EDGE-001",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Aggregation Type Mismatch",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "mismatched_agg_validator",
                        "outcome": "PASS",
                        "measured_value": [3.0, 3.1, 3.2],
                        "units": "V",
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": "string_value",  # String instead of number
                                "outcome": "PASS",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 3.0,
                                        "outcome": "PASS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_aggregation_on_empty_array(client: TofuPilot, procedure_id: str):
    """Test aggregation computed on empty array."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-EMPTY-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGG-EDGE-002",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Empty Array Aggregation",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "empty_data",
                        "outcome": "PASS",
                        "measured_value": [],
                        "aggregations": [
                            {
                                "type": "count",
                                "value": 0,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_aggregation_with_negative_values(client: TofuPilot, procedure_id: str):
    """Test aggregation on negative values."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-AGG-NEGATIVE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-AGG-EDGE-003",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Negative Value Aggregation",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "negative_temps",
                        "outcome": "PASS",
                        "measured_value": [-10.0, -15.0, -12.0, -8.0],
                        "units": "C",
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": -11.25,
                                "outcome": "PASS",
                                "unit": "C"
                            },
                            {
                                "type": "min",
                                "value": -15.0,
                                "outcome": "PASS",
                                "unit": "C"
                            },
                            {
                                "type": "max",
                                "value": -8.0,
                                "outcome": "PASS",
                                "unit": "C"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)
