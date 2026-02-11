"""Test multi-dimensional measurements (MDM) with x_axis/y_axis validators and aggregations.

This test suite covers the structured multi-dimensional data format using x_axis and y_axis
with per-axis validators and aggregations, replacing the legacy multi-dimensional array format.
"""

import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError
from ...utils import get_random_test_dates, assert_create_run_success


# =============================================================================
# BASIC X_AXIS / Y_AXIS STRUCTURE
# =============================================================================


def test_mdm_basic_x_axis_y_axis(client: TofuPilot, procedure_id: str):
    """Test basic x_axis and y_axis structure without validators/aggregations."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-BASIC-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-001",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Basic MDM Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_vs_time",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0, 4.0],
                            "units": "s",
                            "description": "Time"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.2, 3.1],
                                "units": "V",
                                "description": "Voltage"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_mdm_multiple_y_axis_series(client: TofuPilot, procedure_id: str):
    """Test multiple y_axis series (multiple data series against same x_axis)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-MULTI-Y-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-002",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Multiple Y-Axis Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_current_vs_time",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0],
                            "units": "s",
                            "description": "Time"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.1],
                                "units": "V",
                                "description": "Voltage"
                            },
                            {
                                "data": [1.0, 1.2, 1.3, 1.1],
                                "units": "A",
                                "description": "Current"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# X_AXIS WITH VALIDATORS
# =============================================================================


def test_x_axis_with_single_validator(client: TofuPilot, procedure_id: str):
    """Test x_axis with a single validator."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-X-VAL-1-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-003",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "X-Axis Validator Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "time_validated",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0, 4.0],
                            "units": "s",
                            "validators": [
                                {
                                    "operator": ">=",
                                    "expected_value": 0.0,
                                    "outcome": "PASS"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [10.0, 20.0, 30.0, 40.0, 50.0],
                                "units": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_x_axis_with_multiple_validators(client: TofuPilot, procedure_id: str):
    """Test x_axis with multiple validators (range check)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-X-VAL-MULTI-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-004",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "X-Axis Multiple Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "frequency_range_check",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [1.0, 2.0, 3.0, 4.0, 5.0],
                            "units": "kHz",
                            "validators": [
                                {
                                    "operator": ">=",
                                    "expected_value": 0.5,
                                    "outcome": "PASS"
                                },
                                {
                                    "operator": "<=",
                                    "expected_value": 10.0,
                                    "outcome": "PASS"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [100.0, 95.0, 90.0, 85.0, 80.0],
                                "units": "dB"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_x_axis_validator_with_fail_outcome(client: TofuPilot, procedure_id: str):
    """Test x_axis validator that fails."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-X-VAL-FAIL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-005",
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "X-Axis Validator Failure",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "out_of_range_time",
                        "outcome": "FAIL",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 11.0],  # Last value out of range
                            "units": "s",
                            "validators": [
                                {
                                    "operator": "<=",
                                    "expected_value": 10.0,
                                    "outcome": "FAIL",
                                    "is_decisive": True
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [1.0, 2.0, 3.0, 4.0],
                                "units": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# X_AXIS WITH AGGREGATIONS
# =============================================================================


def test_x_axis_with_single_aggregation(client: TofuPilot, procedure_id: str):
    """Test x_axis with a single aggregation."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-X-AGG-1-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-006",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "X-Axis Aggregation Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "time_statistics",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [1.0, 2.0, 3.0, 4.0, 5.0],
                            "units": "s",
                            "aggregations": [
                                {
                                    "type": "avg",
                                    "value": 3.0,
                                    "outcome": "PASS",
                                    "unit": "s"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [10.0, 20.0, 30.0, 40.0, 50.0],
                                "units": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_x_axis_with_multiple_aggregations(client: TofuPilot, procedure_id: str):
    """Test x_axis with multiple aggregations (min, max, avg)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-X-AGG-MULTI-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-007",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "X-Axis Multiple Aggregations",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "frequency_stats",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [1.0, 2.0, 3.0, 4.0, 5.0],
                            "units": "Hz",
                            "aggregations": [
                                {
                                    "type": "min",
                                    "value": 1.0,
                                    "outcome": "PASS",
                                    "unit": "Hz"
                                },
                                {
                                    "type": "max",
                                    "value": 5.0,
                                    "outcome": "PASS",
                                    "unit": "Hz"
                                },
                                {
                                    "type": "avg",
                                    "value": 3.0,
                                    "outcome": "PASS",
                                    "unit": "Hz"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [100.0, 95.0, 90.0, 85.0, 80.0],
                                "units": "dB"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_x_axis_aggregation_with_validators(client: TofuPilot, procedure_id: str):
    """Test x_axis aggregation with nested validators."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-X-AGG-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-008",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "X-Axis Agg with Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "time_avg_validated",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.5, 1.0, 1.5, 2.0, 2.5],
                            "units": "s",
                            "aggregations": [
                                {
                                    "type": "avg",
                                    "value": 1.5,
                                    "outcome": "PASS",
                                    "unit": "s",
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
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.1, 3.2, 3.3, 3.4],
                                "units": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# Y_AXIS WITH VALIDATORS
# =============================================================================


def test_y_axis_with_single_validator(client: TofuPilot, procedure_id: str):
    """Test y_axis with a single validator."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-Y-VAL-1-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-009",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Y-Axis Validator Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_validated",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.1],
                                "units": "V",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 2.8,
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


def test_y_axis_with_multiple_validators(client: TofuPilot, procedure_id: str):
    """Test y_axis with multiple validators (range check)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-Y-VAL-MULTI-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-010",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Y-Axis Multiple Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_range_check",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0, 4.0],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.2, 3.1],
                                "units": "V",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 2.8,
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


def test_multiple_y_axis_each_with_validators(client: TofuPilot, procedure_id: str):
    """Test multiple y_axis series, each with their own validators."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MULTI-Y-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-011",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Multiple Y-Axis with Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_current_validated",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [3.3, 3.4, 3.5],
                                "units": "V",
                                "description": "Voltage",
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
                            },
                            {
                                "data": [1.0, 1.2, 1.1],
                                "units": "A",
                                "description": "Current",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 0.5,
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
            }
        ]
    )

    assert_create_run_success(result)


# =============================================================================
# Y_AXIS WITH AGGREGATIONS
# =============================================================================


def test_y_axis_with_single_aggregation(client: TofuPilot, procedure_id: str):
    """Test y_axis with a single aggregation."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-Y-AGG-1-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-012",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Y-Axis Aggregation Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_average",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0, 4.0],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.4, 3.3, 3.1],
                                "units": "V",
                                "aggregations": [
                                    {
                                        "type": "avg",
                                        "value": 3.2,
                                        "outcome": "PASS",
                                        "unit": "V"
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


def test_y_axis_with_multiple_aggregations(client: TofuPilot, procedure_id: str):
    """Test y_axis with multiple aggregations."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-Y-AGG-MULTI-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-013",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Y-Axis Multiple Aggregations",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "voltage_statistics",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0, 4.0],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.1, 3.2, 3.3, 3.4],
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
                                        "value": 3.4,
                                        "outcome": "PASS",
                                        "unit": "V"
                                    },
                                    {
                                        "type": "avg",
                                        "value": 3.2,
                                        "outcome": "PASS",
                                        "unit": "V"
                                    },
                                    {
                                        "type": "std",
                                        "value": 0.15,
                                        "outcome": "PASS",
                                        "unit": "V"
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


def test_y_axis_aggregation_with_validators(client: TofuPilot, procedure_id: str):
    """Test y_axis aggregation with nested validators."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-Y-AGG-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-014",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Y-Axis Agg with Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "max_voltage_validated",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.5, 3.1],
                                "units": "V",
                                "aggregations": [
                                    {
                                        "type": "max",
                                        "value": 3.5,
                                        "outcome": "PASS",
                                        "unit": "V",
                                        "validators": [
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
            }
        ]
    )

    assert_create_run_success(result)


def test_multiple_y_axis_each_with_aggregations(client: TofuPilot, procedure_id: str):
    """Test multiple y_axis series, each with their own aggregations."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MULTI-Y-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-015",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Multiple Y-Axis with Aggregations",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "dual_channel_stats",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.1],
                                "units": "V",
                                "description": "Voltage",
                                "aggregations": [
                                    {
                                        "type": "avg",
                                        "value": 3.15,
                                        "outcome": "PASS",
                                        "unit": "V"
                                    },
                                    {
                                        "type": "max",
                                        "value": 3.3,
                                        "outcome": "PASS",
                                        "unit": "V"
                                    }
                                ]
                            },
                            {
                                "data": [1.0, 1.1, 1.2, 1.05],
                                "units": "A",
                                "description": "Current",
                                "aggregations": [
                                    {
                                        "type": "avg",
                                        "value": 1.09,
                                        "outcome": "PASS",
                                        "unit": "A"
                                    },
                                    {
                                        "type": "max",
                                        "value": 1.2,
                                        "outcome": "PASS",
                                        "unit": "A"
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
# COMBINED X_AXIS AND Y_AXIS WITH VALIDATORS AND AGGREGATIONS
# =============================================================================


def test_both_axes_with_validators(client: TofuPilot, procedure_id: str):
    """Test both x_axis and y_axis with validators."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-XY-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-016",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Both Axes Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "sweep_test",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [1.0, 2.0, 3.0, 4.0, 5.0],
                            "units": "kHz",
                            "description": "Frequency",
                            "validators": [
                                {
                                    "operator": ">=",
                                    "expected_value": 1.0,
                                    "outcome": "PASS"
                                },
                                {
                                    "operator": "<=",
                                    "expected_value": 5.0,
                                    "outcome": "PASS"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [100.0, 95.0, 90.0, 85.0, 80.0],
                                "units": "dB",
                                "description": "Amplitude",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 75.0,
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


def test_both_axes_with_aggregations(client: TofuPilot, procedure_id: str):
    """Test both x_axis and y_axis with aggregations."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-XY-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-017",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Both Axes Aggregations",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "time_voltage_stats",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0, 4.0],
                            "units": "s",
                            "aggregations": [
                                {
                                    "type": "max",
                                    "value": 4.0,
                                    "outcome": "PASS",
                                    "unit": "s"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.1, 3.2, 3.3, 3.4],
                                "units": "V",
                                "aggregations": [
                                    {
                                        "type": "avg",
                                        "value": 3.2,
                                        "outcome": "PASS",
                                        "unit": "V"
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


def test_comprehensive_mdm_all_features(client: TofuPilot, procedure_id: str):
    """Test comprehensive MDM with all features: x/y axes, validators, aggregations."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-FULL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-018",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Comprehensive MDM Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "full_sweep_analysis",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [1.0, 2.0, 3.0, 4.0, 5.0],
                            "units": "kHz",
                            "description": "Frequency",
                            "validators": [
                                {
                                    "operator": "range",
                                    "expected_value": [1.0, 5.0],
                                    "outcome": "PASS"
                                }
                            ],
                            "aggregations": [
                                {
                                    "type": "avg",
                                    "value": 3.0,
                                    "outcome": "PASS",
                                    "unit": "kHz",
                                    "validators": [
                                        {
                                            "operator": ">=",
                                            "expected_value": 2.5,
                                            "outcome": "PASS"
                                        }
                                    ]
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [100.0, 95.0, 90.0, 92.0, 88.0],
                                "units": "dB",
                                "description": "Channel 1 Amplitude",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 85.0,
                                        "outcome": "PASS"
                                    }
                                ],
                                "aggregations": [
                                    {
                                        "type": "min",
                                        "value": 88.0,
                                        "outcome": "PASS",
                                        "unit": "dB",
                                        "validators": [
                                            {
                                                "operator": ">=",
                                                "expected_value": 85.0,
                                                "outcome": "PASS"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "max",
                                        "value": 100.0,
                                        "outcome": "PASS",
                                        "unit": "dB"
                                    }
                                ]
                            },
                            {
                                "data": [3.0, 3.1, 3.2, 3.15, 3.05],
                                "units": "V",
                                "description": "Supply Voltage",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 2.8,
                                        "outcome": "PASS"
                                    },
                                    {
                                        "operator": "<=",
                                        "expected_value": 3.6,
                                        "outcome": "PASS"
                                    }
                                ],
                                "aggregations": [
                                    {
                                        "type": "avg",
                                        "value": 3.1,
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
                                                "expected_value": 3.3,
                                                "outcome": "PASS"
                                            }
                                        ]
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
# STATION ACCESS CONTROL
# =============================================================================


def test_station_can_create_mdm_with_validators(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can create MDM runs with validators."""
    if auth_type != "station":
        return

    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-STATION-MDM-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Station MDM Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "station_sweep",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [1.0, 2.0, 3.0],
                            "units": "kHz",
                            "validators": [
                                {
                                    "operator": ">=",
                                    "expected_value": 1.0,
                                    "outcome": "PASS"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [100.0, 95.0, 90.0],
                                "units": "dB",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 85.0,
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


def test_station_can_create_mdm_with_aggregations(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can create MDM runs with aggregations."""
    if auth_type != "station":
        return

    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-STATION-MDM-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Station MDM Aggregations",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "station_stats",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0],
                            "units": "s",
                            "aggregations": [
                                {
                                    "type": "max",
                                    "value": 3.0,
                                    "outcome": "PASS",
                                    "unit": "s"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.1],
                                "units": "V",
                                "aggregations": [
                                    {
                                        "type": "avg",
                                        "value": 3.15,
                                        "outcome": "PASS",
                                        "unit": "V"
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


def test_station_can_create_comprehensive_mdm(client: TofuPilot, procedure_id: str, auth_type: str):
    """Test that stations can create comprehensive MDM with all features."""
    if auth_type != "station":
        return

    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-STATION-MDM-FULL-{unique_id}",
        procedure_id=procedure_id,
        part_number=f"TEST-STATION-{unique_id}",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Station Full MDM",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "comprehensive_test",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [1.0, 2.0, 3.0],
                            "units": "kHz",
                            "validators": [
                                {
                                    "operator": "range",
                                    "expected_value": [1.0, 3.0],
                                    "outcome": "PASS"
                                }
                            ],
                            "aggregations": [
                                {
                                    "type": "avg",
                                    "value": 2.0,
                                    "outcome": "PASS",
                                    "unit": "kHz"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [100.0, 95.0, 90.0],
                                "units": "dB",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 85.0,
                                        "outcome": "PASS"
                                    }
                                ],
                                "aggregations": [
                                    {
                                        "type": "min",
                                        "value": 90.0,
                                        "outcome": "PASS",
                                        "unit": "dB",
                                        "validators": [
                                            {
                                                "operator": ">=",
                                                "expected_value": 85.0,
                                                "outcome": "PASS"
                                            }
                                        ]
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
# MEASUREMENT-LEVEL VALIDATORS AND AGGREGATIONS (alongside x_axis/y_axis)
# =============================================================================


def test_mdm_with_measurement_level_validators(client: TofuPilot, procedure_id: str):
    """Test MDM with validators at the measurement level (not inside x_axis/y_axis)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-MEAS-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-MEAS-001",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "MDM Measurement Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "sweep_with_measurement_validators",
                        "outcome": "PASS",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 0,
                                "outcome": "PASS"
                            }
                        ],
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.1],
                                "units": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_mdm_with_measurement_level_aggregations(client: TofuPilot, procedure_id: str):
    """Test MDM with aggregations at the measurement level (not inside x_axis/y_axis)."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-MEAS-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-MEAS-002",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "MDM Measurement Aggregations",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "sweep_with_measurement_aggregations",
                        "outcome": "PASS",
                        "aggregations": [
                            {
                                "type": "avg",
                                "value": 3.15,
                                "outcome": "PASS",
                                "unit": "V"
                            }
                        ],
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.1],
                                "units": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_mdm_with_measurement_and_axis_validators(client: TofuPilot, procedure_id: str):
    """Test MDM with validators at both measurement level and inside axes."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-BOTH-VAL-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-MEAS-003",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "MDM Both Level Validators",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "sweep_all_validators",
                        "outcome": "PASS",
                        "validators": [
                            {
                                "operator": ">=",
                                "expected_value": 0,
                                "outcome": "PASS"
                            }
                        ],
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0],
                            "units": "s",
                            "validators": [
                                {
                                    "operator": ">=",
                                    "expected_value": 0.0,
                                    "outcome": "PASS"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.1],
                                "units": "V",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": 2.8,
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


def test_mdm_with_measurement_and_axis_aggregations(client: TofuPilot, procedure_id: str):
    """Test MDM with aggregations at both measurement level and inside axes."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-BOTH-AGG-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-MEAS-004",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "MDM Both Level Aggregations",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "sweep_all_aggregations",
                        "outcome": "PASS",
                        "aggregations": [
                            {
                                "type": "overall-avg",
                                "value": 3.15,
                                "outcome": "PASS"
                            }
                        ],
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0],
                            "units": "s",
                            "aggregations": [
                                {
                                    "type": "max",
                                    "value": 3.0,
                                    "outcome": "PASS",
                                    "unit": "s"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [3.0, 3.2, 3.3, 3.1],
                                "units": "V",
                                "aggregations": [
                                    {
                                        "type": "avg",
                                        "value": 3.15,
                                        "outcome": "PASS",
                                        "unit": "V"
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
# EDGE CASES - MDM SPECIFIC
# =============================================================================


def test_mdm_mismatched_array_lengths(client: TofuPilot, procedure_id: str):
    """Test MDM where x_axis and y_axis have different lengths."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-LENGTH-MISMATCH-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-EDGE-001",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Mismatched Lengths Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "mismatched_lengths",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [0.0, 1.0, 2.0, 3.0, 4.0],  # 5 points
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [10.0, 20.0, 30.0],  # Only 3 points
                                "units": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_mdm_empty_arrays(client: TofuPilot, procedure_id: str):
    """Test MDM with empty data arrays."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-EMPTY-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-EDGE-002",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Empty Arrays Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "empty_data",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [],
                            "units": "s"
                        },
                        "y_axis": [
                            {
                                "data": [],
                                "units": "V"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    assert_create_run_success(result)


def test_mdm_negative_values_both_axes(client: TofuPilot, procedure_id: str):
    """Test MDM with negative values on both axes."""
    started_at, ended_at = get_random_test_dates()
    unique_id = str(uuid.uuid4())[:8]

    result = client.runs.create(
        serial_number=f"SN-MDM-NEGATIVE-{unique_id}",
        procedure_id=procedure_id,
        part_number="TEST-MDM-EDGE-003",
        started_at=started_at,
        outcome="PASS",
        ended_at=ended_at,
        phases=[
            {
                "name": "Negative Values Test",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {
                        "name": "negative_sweep",
                        "outcome": "PASS",
                        "x_axis": {
                            "data": [-10.0, -5.0, 0.0, 5.0, 10.0],
                            "units": "s",
                            "validators": [
                                {
                                    "operator": ">=",
                                    "expected_value": -15.0,
                                    "outcome": "PASS"
                                }
                            ]
                        },
                        "y_axis": [
                            {
                                "data": [-100.0, -50.0, 0.0, 50.0, 100.0],
                                "units": "mV",
                                "validators": [
                                    {
                                        "operator": ">=",
                                        "expected_value": -150.0,
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
