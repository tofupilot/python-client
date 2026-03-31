"""Test legacy lower_limit/upper_limit compatibility.

This test suite verifies that the legacy lower_limit and upper_limit fields
still work alongside the new validators syntax, ensuring backward compatibility.
"""

import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError
from ...utils import get_random_test_dates, assert_create_run_success


# =============================================================================
# LEGACY LOWER_LIMIT / UPPER_LIMIT
# =============================================================================


def test_legacy_lower_limit_only(client: TofuPilot, procedure_id: str):
    """Test legacy lower_limit field (no upper_limit)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-LOWER-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-001",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Lower Limit Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage",
                        "outcome": "PASS",
                        "measured_value": 3.3,
                        "units": "V",
                        "lower_limit": 3.0
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_legacy_upper_limit_only(client: TofuPilot, procedure_id: str):
    """Test legacy upper_limit field (no lower_limit)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-UPPER-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-002",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Upper Limit Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "current",
                        "outcome": "PASS",
                        "measured_value": 1.5,
                        "units": "A",
                        "upper_limit": 2.0
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_legacy_both_limits(client: TofuPilot, procedure_id: str):
    """Test legacy lower_limit and upper_limit together (range check)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-BOTH-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-003",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Both Limits Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_range",
                        "outcome": "PASS",
                        "measured_value": 3.3,
                        "units": "V",
                        "lower_limit": 3.0,
                        "upper_limit": 3.6
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_legacy_limits_with_failure(client: TofuPilot, procedure_id: str):
    """Test legacy limits with measurement that fails."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-FAIL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-004",
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "Failed Limit Test",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "out_of_range_voltage",
                        "outcome": "FAIL",
                        "measured_value": 3.8,  # Above upper_limit
                        "units": "V",
                        "lower_limit": 3.0,
                        "upper_limit": 3.6
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# LEGACY LIMITS WITH NEW VALIDATORS (COEXISTENCE)
# =============================================================================


def test_legacy_limits_coexist_with_validators(client: TofuPilot, procedure_id: str):
    """Test that legacy limits can coexist with new validators in same run (different measurements)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-COEXIST-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-005",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Coexistence Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "legacy_measurement",
                        "outcome": "PASS",
                        "measured_value": 3.3,
                        "units": "V",
                        "lower_limit": 3.0,
                        "upper_limit": 3.6
                    },
                    {
                        "name": "new_measurement",
                        "outcome": "PASS",
                        "measured_value": 1.5,
                        "units": "A",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 1.0,
                                "outcome": "PASS"
                            },
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


def test_legacy_limits_multiple_measurements(client: TofuPilot, procedure_id: str):
    """Test multiple measurements using legacy limits."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MULTI-LEGACY-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-006",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Multiple Legacy Measurements",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage",
                        "outcome": "PASS",
                        "measured_value": 3.3,
                        "units": "V",
                        "lower_limit": 3.0,
                        "upper_limit": 3.6
                    },
                    {
                        "name": "current",
                        "outcome": "PASS",
                        "measured_value": 1.5,
                        "units": "A",
                        "lower_limit": 1.0,
                        "upper_limit": 2.0
                    },
                    {
                        "name": "temperature",
                        "outcome": "PASS",
                        "measured_value": 25.0,
                        "units": "C",
                        "lower_limit": 20.0,
                        "upper_limit": 30.0
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# LEGACY LIMITS - EDGE CASES
# =============================================================================


def test_legacy_limits_with_negative_values(client: TofuPilot, procedure_id: str):
    """Test legacy limits with negative values."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-NEGATIVE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-007",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Negative Limits Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "offset_voltage",
                        "outcome": "PASS",
                        "measured_value": -5.0,
                        "units": "V",
                        "lower_limit": -10.0,
                        "upper_limit": -2.0
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_legacy_limits_with_zero(client: TofuPilot, procedure_id: str):
    """Test legacy limits with zero as boundary."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-ZERO-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-008",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Zero Boundary Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "error_count",
                        "outcome": "PASS",
                        "measured_value": 0,
                        "lower_limit": 0,
                        "upper_limit": 5
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_legacy_limits_equal_boundaries(client: TofuPilot, procedure_id: str):
    """Test legacy limits where lower_limit equals upper_limit (exact value check)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-EQUAL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-009",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Equal Boundaries Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "exact_voltage",
                        "outcome": "PASS",
                        "measured_value": 5.0,
                        "units": "V",
                        "lower_limit": 5.0,
                        "upper_limit": 5.0
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_legacy_limits_very_small_range(client: TofuPilot, procedure_id: str):
    """Test legacy limits with very small range (tight tolerance)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-TIGHT-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-010",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Tight Tolerance Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "precision_voltage",
                        "outcome": "PASS",
                        "measured_value": 3.3005,
                        "units": "V",
                        "lower_limit": 3.3,
                        "upper_limit": 3.301
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# LEGACY LIMITS - DIFFERENT DATA TYPES
# =============================================================================


def test_legacy_limits_integer_values(client: TofuPilot, procedure_id: str):
    """Test legacy limits with integer values."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-INT-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-011",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Integer Limits Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "pin_count",
                        "outcome": "PASS",
                        "measured_value": 24,
                        "lower_limit": 20,
                        "upper_limit": 30
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_legacy_limits_float_precision(client: TofuPilot, procedure_id: str):
    """Test legacy limits with high-precision float values."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-LEGACY-FLOAT-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-012",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Float Precision Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "resistance",
                        "outcome": "PASS",
                        "measured_value": 100.12345,
                        "units": "Ohm",
                        "lower_limit": 100.0,
                        "upper_limit": 100.5
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# STATION ACCESS CONTROL - LEGACY LIMITS
# =============================================================================


def test_station_can_create_run_with_legacy_limits(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can create runs with legacy lower_limit/upper_limit."""
    if auth_type != "station":
        return

    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-STATION-LEGACY-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Station Legacy Limits",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage",
                        "outcome": "PASS",
                        "measured_value": 3.3,
                        "units": "V",
                        "lower_limit": 3.0,
                        "upper_limit": 3.6
                    },
                    {
                        "name": "current",
                        "outcome": "PASS",
                        "measured_value": 1.5,
                        "units": "A",
                        "lower_limit": 1.0,
                        "upper_limit": 2.0
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# MIGRATION SCENARIOS
# =============================================================================


def test_migration_from_legacy_to_new_syntax(client: TofuPilot, procedure_id: str):
    """Test migration scenario: same measurement name used with both syntaxes across different runs."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    # First run with legacy syntax
    result1 = client.runs.create(
        serial_number=f"SN-MIGRATE-1-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MIGRATE-001",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Migration Test Phase",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "supply_voltage",
                        "outcome": "PASS",
                        "measured_value": 3.3,
                        "units": "V",
                        "lower_limit": 3.0,
                        "upper_limit": 3.6
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result1)

    # Second run with new syntax (same measurement name)
    result2 = client.runs.create(
        serial_number=f"SN-MIGRATE-2-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MIGRATE-001",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Migration Test Phase",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "supply_voltage",  # Same name as above
                        "outcome": "PASS",
                        "measured_value": 3.4,
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

    assert_create_run_success(result2)


def test_backward_compatibility_multiple_phases(client: TofuPilot, procedure_id: str):
    """Test backward compatibility across multiple phases with legacy syntax."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-BACK-COMPAT-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-LEGACY-013",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Power Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage",
                        "outcome": "PASS",
                        "measured_value": 3.3,
                        "units": "V",
                        "lower_limit": 3.0,
                        "upper_limit": 3.6
                    }
                ]
            },
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
                        "lower_limit": 1.0,
                        "upper_limit": 2.0
                    }
                ]
            },
            {
                "name": "Temperature Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "temperature",
                        "outcome": "PASS",
                        "measured_value": 25.0,
                        "units": "C",
                        "lower_limit": 20.0,
                        "upper_limit": 30.0
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)
