"""Test run creation with both phases and steps (mixed legacy support)."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, client


class TestCreateRunPhasesAndSteps:

    def test_run_creation_with_phases_and_steps(self, client: TofuPilotClient, procedure_identifier):
        """Test run creation with both phases and steps (mixed legacy support)."""
        # Adapted from https://github.com/tofupilot/examples/blob/5cf044d0e55c11ea55114014edb206605689aa6d/qa/client/create_run/with_phases_and_steps/main.py

        # Reference time to calculate start_time_millis in milliseconds since epoch
        epoch = datetime(1970, 1, 1)

        # Function to calculate milliseconds since epoch
        def to_millis(dt):
            return int((dt - epoch).total_seconds() * 1000)

        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={
                "serial_number": "SN17",
                "part_number": "PNrstsrtsr",
                "batch_number": "B",
            },
            run_passed=True,  # Overall run status
            steps=[
                {
                    "name": "step_connect",  # First step
                    "step_passed": True,  # Status of the step
                    # Duration of the step
                    "duration": timedelta(seconds=5, milliseconds=12),
                    "started_at": datetime.now(),  # Start time of the step
                },
                {
                    "name": "step_string2",  # First step
                    "step_passed": True,  # Status of the step
                    # Duration of the step
                    "duration": timedelta(seconds=5, milliseconds=12),
                    "started_at": datetime.now(),  # Start time of the step
                    "measurement_value": "This is a string",
                },
                {
                    "name": "step_initial_charge_check",  # Second step
                    "step_passed": True,  # Status of the step
                    "duration": timedelta(
                        seconds=3, milliseconds=100
                    ),  # Duration of the step (<1s)
                    "started_at": datetime.now()
                    + timedelta(seconds=3),  # Start time of the second step
                    "measurement_value": 99,  # Measured value
                },
                {
                    "name": "step_initial_temp_check",  # Third step
                    "step_passed": True,  # Status of the step
                    "duration": timedelta(
                        seconds=1, milliseconds=100
                    ),  # Duration of the step (<1s)
                    "started_at": datetime.now()
                    # Start time of the third step
                    + timedelta(seconds=2, milliseconds=500),
                    "measurement_value": -1,  # Measured temperature value
                    "measurement_unit": "°C",  # Unit of the measurement (temperature)
                    "limit_low": 0,  # Lower limit of acceptable temperature
                },
                {
                    "name": "step_temp_calibration",  # Fourth step
                    "step_passed": False,  # Status of the step
                    "duration": timedelta(
                        seconds=3, milliseconds=100
                    ),  # Duration of the step (<1s)
                    "started_at": datetime.now() - timedelta(days=1, minutes=20),
                    "measurement_value": 69,  # Measured temperature value after calibration
                    "measurement_unit": "°C",  # Unit of the measurement (temperature)
                    "limit_low": 70,  # Lower limit of acceptable temperature
                    "limit_high": 80,  # Upper limit of acceptable temperature
                },
            ],
            phases=[
                {
                    "name": "phase_connect",  # First phase
                    "outcome": "PASS",
                    "start_time_millis": to_millis(
                        datetime.now()
                    ),  # Start time of the step in ms
                    "end_time_millis": to_millis(
                        datetime.now() + timedelta(seconds=5, milliseconds=12)
                    ),  # End time in ms
                    "measurements": [
                        {
                            "name": "connectivity_check",
                            "outcome": "PASS",  # Measurement outcome
                            "measured_value": None,
                            "units": None,
                            "lower_limit": None,
                            "upper_limit": None,
                        }
                    ],
                },
                {
                    "name": "phase_initial_charge_check",  # Second phase
                    "outcome": "PASS",
                    "start_time_millis": to_millis(
                        datetime.now() + timedelta(seconds=3)
                    ),  # Start time in ms
                    "end_time_millis": to_millis(
                        datetime.now() + timedelta(seconds=6, milliseconds=100)
                    ),  # End time in ms
                    "measurements": [
                        {
                            "name": "initial_charge",
                            "outcome": "PASS",  # Measurement outcome
                            "measured_value": 97,  # Measured value
                            "units": None,
                            "lower_limit": None,
                            "upper_limit": None,
                        },
                        {
                            "name": "initial_temperature",
                            "outcome": "PASS",  # Measurement outcome
                            # Measured temperature value
                            "measured_value": 18,
                            "units": "°C",  # Unit of the measurement
                            "lower_limit": 0,  # Lower limit
                            "upper_limit": None,
                        },
                        {
                            "name": "initial_temperature_2",
                            "outcome": "FAIL",  # Measurement outcome
                            # Measured temperature value
                            "measured_value": 14,
                            "units": "°C",  # Unit of the measurement
                            "lower_limit": 0,  # Lower limit
                            "upper_limit": 15,  # Upper limit
                        },
                    ],
                },
                {
                    "name": "phase_initial_temp_check",  # Third phase
                    "outcome": "PASS",
                    "start_time_millis": to_millis(
                        datetime.now() + timedelta(seconds=2, milliseconds=500)
                    ),  # Start time in ms
                    "end_time_millis": to_millis(
                        datetime.now() + timedelta(seconds=3, milliseconds=600)
                    ),  # End time in ms
                    "measurements": [
                        {
                            "name": "initial_temperature",
                            "outcome": "PASS",  # Measurement outcome
                            # Measured temperature value
                            "measured_value": 1,
                            "units": "°C",  # Unit of the measurement
                            "lower_limit": 0,  # Lower limit
                            "upper_limit": None,
                        }
                    ],
                },
                {
                    "name": "phase_temp_calibration",  # Fourth phase
                    "outcome": "FAIL",
                    "start_time_millis": to_millis(
                        datetime.now() - timedelta(days=1, minutes=20)
                    ),  # Start time in ms
                    "end_time_millis": to_millis(
                        datetime.now()
                        - timedelta(days=1, minutes=20)
                        + timedelta(seconds=3, milliseconds=100)
                    ),  # End time in ms
                    "measurements": [
                        {
                            "name": "temperature_calibration",
                            "outcome": "FAIL",  # Measurement outcome
                            "measured_value": 81,  # Measured value
                            "units": "°C",  # Unit of the measurement
                            "lower_limit": 70,  # Lower limit
                            "upper_limit": 80,
                        }
                    ],
                },
            ],
        )

        assert_create_run_success(result)