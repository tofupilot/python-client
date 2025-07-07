"""
Test against local TofuPilot server running on localhost:3000.

This test is designed to run against a local development instance of TofuPilot.
It requires:
1. TofuPilot server running on http://localhost:3000
2. Valid API key set in TOFUPILOT_API_KEY environment variable
3. Network connectivity to localhost
"""

import pytest
import os
import inspect
from datetime import datetime, timedelta
import time

from tofupilot.client import TofuPilotClient
from .utils import client, assert_create_run_success
from tofupilot.models.models import (
    UnitUnderTest,
    Phase,
    Measurement,
    Log,
    PhaseOutcome,
    MeasurementOutcome,
    LogLevel,
    SubUnit,
    Step
)

from typing import cast


class TestCreateRun:
    
    @pytest.fixture(params=[
        {},
        {
            "part_name": "Number One",
            "revision": "1",
            "batch_number": "1",
        },
    ])
    def unit_under_test(self, request) -> UnitUnderTest:
        return {
            "serial_number": "AutomatedTest",
            "part_number": "#1",
            **request.param  # pyright: ignore[reportReturnType]
        }
    
    @pytest.fixture(params=[True, False])
    def run_passed(self, request) -> bool:
        return request.param

    def test_minimal(self, client: TofuPilotClient, procedure_identifier, unit_under_test, run_passed):
        """Test minimal run creation with just required parameters."""
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test=unit_under_test,
            run_passed=run_passed,
        )
        
        # Verify successful response
        assert_create_run_success(result)

    def test_with_phases(self, client: TofuPilotClient, procedure_identifier, run_passed):
        """Test run creation with phases and measurements."""
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Phases", "part_number": "#1"},
            run_passed=run_passed,
            phases=[
                Phase(
                    name="Initialization",
                    outcome=PhaseOutcome.PASS,
                    start_time_millis=int((datetime.now() - timedelta(seconds=10)).timestamp() * 1000),
                    end_time_millis=int(datetime.now().timestamp() * 1000),
                    measurements=[
                        Measurement(
                            name="Voltage Check",
                            measured_value=12.5,
                            units="V",
                            outcome=MeasurementOutcome.PASS
                        )
                    ]
                )
            ]
        )
        
        assert_create_run_success(result)

    def test_with_steps(self, client: TofuPilotClient, procedure_identifier, run_passed):
        """Test run creation with deprecated steps parameter."""
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Steps", "part_number": "#1"},
            run_passed=run_passed,
            steps=[
                Step(
                    name="voltage_measurement",
                    started_at=datetime.now(),
                    duration=timedelta(seconds=2.5),
                    step_passed=True,
                    measurement_unit="V",
                    measurement_value=3.3,
                    limit_low=3.0,
                    limit_high=3.6
                )
            ]
        )
        
        assert_create_run_success(result)

    def test_with_timing(self, client: TofuPilotClient, procedure_identifier, run_passed):
        """Test run creation with timing parameters."""
        start_time = datetime.now() - timedelta(minutes=10)
        end_time = datetime.now()
        
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Timing", "part_number": "#1"},
            run_passed=run_passed,
            started_at=start_time,
            duration=end_time - start_time,
        )
        
        assert_create_run_success(result)

    def test_with_sub_units_and_logs(self, client: TofuPilotClient, procedure_identifier, run_passed):
        """Test run creation with sub-units and logs."""
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_SubLogs", "part_number": "#1"},
            run_passed=run_passed,
            sub_units=[
                SubUnit(
                    serial_number="SUB001"
                )
            ],
            logs=[
                Log(
                    message="Test started",
                    level=LogLevel.INFO,
                    timestamp="2024-06-30T12:00:00.000Z",
                    source_file=os.path.basename(inspect.getfile(inspect.currentframe())),
                    line_number=inspect.currentframe().f_lineno
                ),
                Log(
                    message="Warning during test",
                    level=LogLevel.WARNING,
                    timestamp="2024-06-30T12:00:05.000Z",
                    source_file=os.path.basename(inspect.getfile(inspect.currentframe())),
                    line_number=inspect.currentframe().f_lineno
                )
            ]
        )
        
        assert_create_run_success(result)

    def test_multiple_sub_units(self, client: TofuPilotClient, procedure_identifier):
        # Adapted from https://github.com/tofupilot/examples/blob/5cf044d0e55c11ea55114014edb206605689aa6d/qa/client/create_run/multiple_sub_units/main.py
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "00003", "part_number": "SI002"},
            run_passed=True,
            sub_units=[{"serial_number": "00002"}, {"serial_number": "00102"}],
        )
        assert_create_run_success(result)
    
    def test_phase_string_outcomes(self, client: TofuPilotClient, procedure_identifier, run_passed):
        # Adapted from https://github.com/tofupilot/examples/blob/main/qa/client/create_run/phases_string_outcome/main.py

        def flash_firmware():
            measured_value = "1.2.4" if run_passed else "1.2.0"
            return run_passed, measured_value, None, None, None

        serial_number = f"SI0364A1103"

        start_time = int(time.time() * 1000)
        passed, measured_value, unit, limit_low, limit_high = flash_firmware()
        end_time = int(time.time() * 1000)

        outcome = "PASS" if passed else "FAIL"

        phase: Phase = {
            "name": "flash_firmware",
            "outcome": outcome,
            "start_time_millis": start_time,
            "end_time_millis": end_time,
            "measurements": [
                {
                    "name": "flash_firmware",
                    "outcome": outcome,
                    "measured_value": measured_value,
                    "units": unit,
                    "lower_limit": limit_low,
                    "upper_limit": limit_high,
                }
            ],
        }

        result = client.create_run(
            procedure_id=procedure_identifier,
            procedure_name="Test_QA",
            unit_under_test={
                "part_number": "SI03645A",
                "part_name": "test-QA",
                "revision": "3.1",
                "batch_number": "11-24",
                "serial_number": serial_number,
            },
            run_passed=passed,
            phases=[phase],
        )
        assert_create_run_success(result)

    @pytest.fixture(params=[3, 3.1, 3.9, 4])
    def voltage(self, request) -> bool:
        return request.param

    def test_procedure_version(self, client: TofuPilotClient, procedure_identifier, voltage):
        # adapted from https://github.com/tofupilot/examples/blob/5cf044d0e55c11ea55114014edb206605689aa6d/qa/client/create_run/procedure_version/main.py
        
        # Generate SN
        serial_number = f"SI0364A084561"

        # 1 Phase test
        start_time_millis = int(time.time() * 1000)
        limits = {"limit_low": 3.1, "limit_high": 3.5}
        passed = limits["limit_low"] <= voltage <= limits["limit_high"]
        outcome = {True: "PASS", False: "FAIL"}[passed]
        end_time_millis = int(time.time() * 1000)

        result = client.create_run(
            unit_under_test={
                "part_number": "SI0364",
                "serial_number": serial_number,
                "revision": "A",
            },
            procedure_id=procedure_identifier,  # First create procedure in Application
            procedure_version="1.2.20",  # Create procedure version
            phases=[
                {
                    "name": "test_voltage",
                    "outcome": outcome,
                    "start_time_millis": start_time_millis,
                    "end_time_millis": end_time_millis,
                    "measurements": [
                        {
                            "name": "voltage_input",
                            "outcome": outcome,
                            "measured_value": voltage,
                            "units": "V",
                            "lower_limit": limits["limit_low"],
                            "upper_limit": limits["limit_high"],
                        },
                    ],
                },
            ],
            run_passed=passed,
        )
        assert_create_run_success(result)

    def test_with_all_types_of_phases(self, client: TofuPilotClient, procedure_identifier):
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
                            "name": "numeric_measurement",
                            "outcome": "PASS",
                            "measured_value": 12,
                            "units": "Hertz",
                            "lower_limit": 1,
                            "upper_limit": 20,
                        },
                        {
                            "name": "string_measurement",
                            "outcome": "PASS",
                            "measured_value": "Test value",
                            "units": "Unitless",
                            "docstring": "This is a string measurement example",
                        },
                        {
                            "name": "boolean_measurement_true",
                            "outcome": "PASS",
                            "measured_value": True,
                            "units": "BooleanUnit",
                            "docstring": "This is a boolean measurement example",
                        },
                        {
                            "name": "boolean_measurement_false",
                            "outcome": "PASS",
                            "measured_value": False,
                            "units": "BooleanUnit",
                            "docstring": "This is a boolean measurement example",
                        },
                        {
                            "name": "json_measurement",
                            "outcome": "PASS",
                            "measured_value": {"key1": "value1", "key2": 42},
                            "units": "JSONUnit",
                            "docstring": "This is a JSON measurement example",
                        },
                        {
                            "name": "empty_measurement",
                            "outcome": "PASS",
                            "measured_value": None,
                            "units": "EmptyUnit",
                            "docstring": "This is a measurement with a null value",
                        },
                        {
                            "name": "no_value_measurement",
                            "outcome": "PASS",
                            "units": "NoValueUnit",
                            "docstring": "This is a measurement with no value specified",
                        },
                    ],
                }
            ],
        )
        assert_create_run_success(result)

    def test_with_attachments(self, client: TofuPilotClient, procedure_identifier):
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
            run_passed=True,
            attachments=[
                "tests/v1/attachments/temperature-map.png",
                "tests/v1/attachments/performance-report.pdf",
            ],
        )
        assert_create_run_success(result)

    def test_with_phases_and_steps(self, client: TofuPilotClient, procedure_identifier):
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

    def test_comprehensive(self, client: TofuPilotClient, procedure_identifier, run_passed):
        """Test run creation with all possible parameters filled."""
        start_time = datetime.now() - timedelta(minutes=5)
        end_time = datetime.now()
        
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={
                "serial_number": "AutomatedTest_Comprehensive",
                "part_number": "#1",
                "part_name": "Comprehensive Test Unit",
                "revision": "2.0",
                "batch_number": "BATCH001"
            },
            run_passed=run_passed,
            procedure_name="Comprehensive Test Procedure",
            procedure_version="2.1.0",
            phases=[
                Phase(
                    name="Full Test Phase",
                    outcome=PhaseOutcome.PASS,
                    start_time_millis=int(start_time.timestamp() * 1000),
                    end_time_millis=int(end_time.timestamp() * 1000),
                    measurements=[
                        Measurement(
                            name="Multi-Measurement",
                            measured_value=15.7,
                            units="A",
                            outcome=MeasurementOutcome.PASS
                        )
                    ]
                )
            ],
            started_at=start_time,
            duration=end_time - start_time,
            sub_units=[SubUnit(serial_number="COMP_SUB001")],
            attachments=[
                "tests/v1/attachments/temperature-map.png",
                "tests/v1/attachments/performance-report.pdf",
            ],
            logs=[
                Log(
                    message="Comprehensive test executed",
                    level=LogLevel.INFO,
                    timestamp="2024-06-30T12:00:00.000Z",
                    source_file=os.path.basename(inspect.getfile(inspect.currentframe())),
                    line_number=inspect.currentframe().f_lineno
                )
            ]
        )
        
        assert_create_run_success(result)
