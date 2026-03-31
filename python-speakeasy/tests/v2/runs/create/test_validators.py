"""Test basic validator syntax for run creation.

This test suite covers the new structured validator syntax with operator and expected_value,
replacing the legacy lower_limit/upper_limit fields.
"""

import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError
from ...utils import get_random_test_dates, assert_create_run_success, assert_station_access_forbidden


# =============================================================================
# BASIC VALIDATOR OPERATORS
# =============================================================================


def test_validator_greater_than_or_equal(client: TofuPilot, procedure_id: str):
    """Test validator with >= operator."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-GTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-001",
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
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)
    assert result.id is not None


def test_validator_less_than_or_equal(client: TofuPilot, procedure_id: str):
    """Test validator with <= operator."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-002",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Current Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "current",
                        "outcome": "PASS",
                        "measured_value": 1.5,
                        "units": "A",
                        "validators": [
                            {
                                "operator": "<=",
                                "expected_value": 2.0,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_greater_than(client: TofuPilot, procedure_id: str):
    """Test validator with > operator."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-003",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Temperature Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "temperature",
                        "outcome": "PASS",
                        "measured_value": 25.5,
                        "units": "C",
                        "validators": [
                            {
                                "operator": ">",
                                "expected_value": 20.0,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_less_than(client: TofuPilot, procedure_id: str):
    """Test validator with < operator."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-004",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Pressure Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "pressure",
                        "outcome": "PASS",
                        "measured_value": 98.5,
                        "units": "kPa",
                        "validators": [
                            {
                                "operator": "<",
                                "expected_value": 100.0,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_equals(client: TofuPilot, procedure_id: str):
    """Test validator with == operator for numeric values."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-005",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Count Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "pin_count",
                        "outcome": "PASS",
                        "measured_value": 24,
                        "validators": [
                            {
                                "operator": "==",
                                "expected_value": 24,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_not_equals(client: TofuPilot, procedure_id: str):
    """Test validator with != operator."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-006",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Error Code Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "error_code",
                        "outcome": "PASS",
                        "measured_value": 0,
                        "validators": [
                            {
                                "operator": "!=",
                                "expected_value": -1,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_string_equals(client: TofuPilot, procedure_id: str):
    """Test validator with == operator for string values."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-007",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Firmware Version Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "firmware_version",
                        "outcome": "PASS",
                        "measured_value": "1.2.3",
                        "validators": [
                            {
                                "operator": "==",
                                "expected_value": "1.2.3",
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_matches_regex(client: TofuPilot, procedure_id: str):
    """Test validator with matches operator for regex patterns."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-008",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Serial Format Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "serial_format",
                        "outcome": "PASS",
                        "measured_value": "ABC-12345",
                        "validators": [
                            {
                                "operator": "matches",
                                "expected_value": r"^[A-Z]{3}-\d{5}$",
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_in_list(client: TofuPilot, procedure_id: str):
    """Test validator with in operator for list membership."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-009",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "State Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "state",
                        "outcome": "PASS",
                        "measured_value": "ready",
                        "validators": [
                            {
                                "operator": "in",
                                "expected_value": ["ready", "idle", "active"],
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_not_in_list(client: TofuPilot, procedure_id: str):
    """Test validator with not in operator for list exclusion."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-NOT-IN-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-NOT-IN",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "State Exclusion Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "state",
                        "outcome": "PASS",
                        "measured_value": "ready",
                        "validators": [
                            {
                                "operator": "not in",
                                "expected_value": ["error", "failed", "unknown"],
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_range(client: TofuPilot, procedure_id: str):
    """Test validator with range operator."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-010",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Voltage Range Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_range",
                        "outcome": "PASS",
                        "measured_value": 3.3,
                        "units": "V",
                        "validators": [
                            {
                                "operator": "range",
                                "expected_value": [3.0, 3.6],
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# MULTIPLE VALIDATORS
# =============================================================================


def test_multiple_validators_on_single_measurement(client: TofuPilot, procedure_id: str):
    """Test multiple validators on a single measurement (e.g., range check)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-011",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Multi-Validator Test",
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
    )

    assert_create_run_success(result)


def test_multiple_validators_with_mixed_outcomes(client: TofuPilot, procedure_id: str):
    """Test multiple validators where some pass and some fail."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-012",
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "Mixed Outcome Test",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "out_of_spec_voltage",
                        "outcome": "FAIL",
                        "measured_value": 3.7,
                        "units": "V",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 3.0,
                                "outcome": "PASS"
                            },
                            {
                                "operator": "<=",
                                "expected_value": 3.6,
                                "outcome": "FAIL"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# VALIDATOR OUTCOMES
# =============================================================================


def test_validator_outcome_pass(client: TofuPilot, procedure_id: str):
    """Test validator with PASS outcome."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-013",
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
                        "name": "test_value",
                        "outcome": "PASS",
                        "measured_value": 100,
                        "validators": [
                            {
                                "operator": "==",
                                "expected_value": 100,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_outcome_fail(client: TofuPilot, procedure_id: str):
    """Test validator with FAIL outcome."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-014",
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
                        "name": "test_value",
                        "outcome": "FAIL",
                        "measured_value": 150,
                        "validators": [
                            {
                                "operator": "<=",
                                "expected_value": 100,
                                "outcome": "FAIL"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_outcome_unset(client: TofuPilot, procedure_id: str):
    """Test validator with UNSET outcome (no validation performed)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-015",
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
                        "name": "test_value",
                        "outcome": "UNSET",
                        "measured_value": 50,
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 0,
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
# EXPRESSION-ONLY VALIDATORS
# =============================================================================


def test_expression_only_validator(client: TofuPilot, procedure_id: str):
    """Test validator with only expression field (no operator/expected_value)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-016",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Expression Only Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "custom_check",
                        "outcome": "PASS",
                        "measured_value": 42,
                        "validators": [
                            {
                                "expression": "custom_validation_function(x) == True",
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_with_custom_expression_and_operator(client: TofuPilot, procedure_id: str):
    """Test validator with both operator and custom expression field."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-017",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Custom Expression Test",
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
                                "expression": "voltage >= 3.0V (nominal)",
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# IS_DECISIVE FIELD
# =============================================================================


def test_validator_is_decisive_true(client: TofuPilot, procedure_id: str):
    """Test validator with is_decisive=true (validator caused measurement failure)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-018",
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "Fail Measurement Test",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "critical_voltage",
                        "outcome": "FAIL",
                        "measured_value": 2.5,
                        "units": "V",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 3.0,
                                "outcome": "FAIL",
                                "is_decisive": True
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_is_decisive_false(client: TofuPilot, procedure_id: str):
    """Test validator with is_decisive=false (indicative only, doesn't cause failure)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-019",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Warning Validator Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "optional_check",
                        "outcome": "PASS",
                        "measured_value": 2.8,
                        "units": "V",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 3.0,
                                "outcome": "FAIL",
                                "is_decisive": False  # Warning only, doesn't fail measurement
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validators_mixed_is_decisive(client: TofuPilot, procedure_id: str):
    """Test multiple validators with different is_decisive values."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-020",
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "Mixed DFM Test",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage",
                        "outcome": "FAIL",
                        "measured_value": 3.7,
                        "units": "V",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 3.0,
                                "outcome": "PASS",
                                "is_decisive": False
                            },
                            {
                                "operator": "<=",
                                "expected_value": 3.6,
                                "outcome": "FAIL",
                                "is_decisive": True  # This one caused the failure
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# BOOLEAN VALIDATORS
# =============================================================================


def test_validator_boolean_equals_true(client: TofuPilot, procedure_id: str):
    """Test validator with boolean expected_value = true."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-021",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Boolean Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "connection_status",
                        "outcome": "PASS",
                        "measured_value": True,
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
    )

    assert_create_run_success(result)


def test_validator_boolean_equals_false(client: TofuPilot, procedure_id: str):
    """Test validator with boolean expected_value = false."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-022",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Boolean False Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "error_flag",
                        "outcome": "PASS",
                        "measured_value": False,
                        "validators": [
                            {
                                "operator": "==",
                                "expected_value": False,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# NULL/EMPTY VALIDATORS
# =============================================================================


def test_measurement_with_no_validators(client: TofuPilot, procedure_id: str):
    """Test measurement without any validators (omitted field)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-023",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "No Validator Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "unvalidated_value",
                        "outcome": "UNSET",
                        "measured_value": 42.0
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_measurement_with_empty_validators_array(client: TofuPilot, procedure_id: str):
    """Test measurement with empty validators array."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-LTE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-024",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Empty Validators Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "empty_validators",
                        "outcome": "UNSET",
                        "measured_value": 3.3,
                        "validators": []
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_measurement_with_null_validators(client: TofuPilot, procedure_id: str):
    """Test measurement with null validators field."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-NULL-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-VALIDATOR-025",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Null Validators Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "null_validators",
                        "outcome": "UNSET",
                        "measured_value": 3.3,
                        "validators": None
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# STATION ACCESS CONTROL
# =============================================================================


def test_station_can_create_run_with_validators(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can create runs with validators on linked procedures."""
    if auth_type != "station":
        # This test is only for station authentication
        return
    
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    # Stations should be able to create runs with validators
    result = client.runs.create(
        serial_number=f"SN-STATION-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Station Validator Test",
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
    )

    assert_create_run_success(result)
    assert result.id is not None


def test_station_can_create_run_with_expression_only_validators(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can create runs with expression-only validators."""
    if auth_type != "station":
        return
    
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-STATION-EXPR-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Station Expression Validator",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "custom_check",
                        "outcome": "PASS",
                        "measured_value": 42,
                        "validators": [
                            {
                                "expression": "custom_validation(x) == True",
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_station_can_create_run_with_multiple_validators(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can create runs with multiple validators per measurement."""
    if auth_type != "station":
        return
    
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-STATION-MULTI-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "Station Multi Validator",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage",
                        "outcome": "FAIL",
                        "measured_value": 3.8,
                        "units": "V",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 3.0,
                                "outcome": "PASS"
                            },
                            {
                                "operator": "<=",
                                "expected_value": 3.6,
                                "outcome": "FAIL",
                                "is_decisive": True
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_station_can_create_run_with_all_validator_types(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can use all validator operator types."""
    if auth_type != "station":
        return
    
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-STATION-ALL-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "All Validator Types",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "numeric_gte",
                        "outcome": "PASS",
                        "measured_value": 5.0,
                        "validators": [{"operator": ">=", "expected_value": 3.0, "outcome": "PASS"}]
                    },
                    {
                        "name": "numeric_lte",
                        "outcome": "PASS",
                        "measured_value": 2.0,
                        "validators": [{"operator": "<=", "expected_value": 5.0, "outcome": "PASS"}]
                    },
                    {
                        "name": "string_eq",
                        "outcome": "PASS",
                        "measured_value": "OK",
                        "validators": [{"operator": "==", "expected_value": "OK", "outcome": "PASS"}]
                    },
                    {
                        "name": "string_match",
                        "outcome": "PASS",
                        "measured_value": "ABC-123",
                        "validators": [{"operator": "matches", "expected_value": r"^[A-Z]{3}-\d{3}$", "outcome": "PASS"}]
                    },
                    {
                        "name": "in_list",
                        "outcome": "PASS",
                        "measured_value": "active",
                        "validators": [{"operator": "in", "expected_value": ["active", "ready", "idle"], "outcome": "PASS"}]
                    },
                    {
                        "name": "range_check",
                        "outcome": "PASS",
                        "measured_value": 50,
                        "validators": [{"operator": "range", "expected_value": [0, 100], "outcome": "PASS"}]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# EDGE CASES - TYPE MISMATCHES
# =============================================================================


def test_validator_numeric_operator_with_string_value(client: TofuPilot, procedure_id: str):
    """Test numeric operator with string expected_value (type mismatch)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    # Server should accept this and store it (may fall back to expression-only)
    result = client.runs.create(
        serial_number=f"SN-TYPE-MISMATCH-1-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-EDGE-001",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Type Mismatch Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "mismatched_validator",
                        "outcome": "PASS",
                        "measured_value": 3.3,
                        "units": "V",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": "not a number",  # Type mismatch
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_matches_operator_with_numeric_value(client: TofuPilot, procedure_id: str):
    """Test matches operator (string) with numeric expected_value (type mismatch)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-TYPE-MISMATCH-2-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-EDGE-002",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Matches Mismatch Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "mismatched_matches",
                        "outcome": "PASS",
                        "measured_value": "test",
                        "validators": [
                            {
                                "operator": "matches",
                                "expected_value": 123,  # Should be string
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_boolean_on_numeric_measurement(client: TofuPilot, procedure_id: str):
    """Test boolean validator on numeric measurement value."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-BOOL-ON-NUM-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-EDGE-003",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Bool on Numeric Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "numeric_with_bool",
                        "outcome": "PASS",
                        "measured_value": 1,
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
    )

    assert_create_run_success(result)


def test_validator_numeric_on_string_measurement(client: TofuPilot, procedure_id: str):
    """Test numeric validator on string measurement value."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-NUM-ON-STR-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-EDGE-004",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Numeric on String Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "string_with_numeric_validator",
                        "outcome": "PASS",
                        "measured_value": "hello",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 10,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_on_json_measurement(client: TofuPilot, procedure_id: str):
    """Test validator on JSON/object measurement value."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-VAL-ON-JSON-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-EDGE-005",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Validator on JSON Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "json_measurement",
                        "outcome": "PASS",
                        "measured_value": {"key": "value", "nested": {"data": 123}},
                        "validators": [
                            {
                                "operator": "==",
                                "expected_value": 100,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_with_very_large_number(client: TofuPilot, procedure_id: str):
    """Test validator with very large numeric values."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LARGE-NUM-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-EDGE-006",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Large Number Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "large_value",
                        "outcome": "PASS",
                        "measured_value": 9999999999999999,
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 1000000000000000,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_validator_with_negative_numbers(client: TofuPilot, procedure_id: str):
    """Test validator with negative numeric values."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-NEGATIVE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-EDGE-007",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Negative Number Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "negative_value",
                        "outcome": "PASS",
                        "measured_value": -15.5,
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": -20.0,
                                "outcome": "PASS"
                            },
                            {
                                "operator": "<=",
                                "expected_value": -10.0,
                                "outcome": "PASS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)
