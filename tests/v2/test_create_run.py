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

import tofupilot
from .utils import client, assert_create_run_success, assert_get_runs_success, assert_delete_runs_success
from tofupilot.v2.types import (
    UnitUnderTest,
    Phase,
    Measurement,
    Log,
    PhaseOutcome,
    MeasurementOutcome,
    LogLevel,
    SubUnit,
    Step,
    GetRunsResponse
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

    def test_minimal(self, client: tofupilot.v2.Client, procedure_identifier, unit_under_test, run_passed):
        """Test minimal run creation with just required parameters."""
        result = client.runs.create(
            procedure_id=procedure_identifier,
            unit_under_test=unit_under_test,
            run_passed=run_passed,
        )
        
        # Verify successful response
        assert_create_run_success(result)

    def test_with_phases(self, client: tofupilot.v2.Client, procedure_identifier, run_passed):
        """Test run creation with phases and measurements."""
        result = client.runs.create(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Phases", "part_number": "#1"},
            run_passed=run_passed,
            phases=[
                Phase(
                    name="Initialization",
                    outcome=PhaseOutcome.PASS,
                    start_time=datetime.now() - timedelta(seconds=10),
                    end_time=datetime.now(),
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

    def test_with_old_phases(self, client: tofupilot.v2.Client, procedure_identifier, run_passed):
        """Test run creation with phases and measurements."""
        result = client.runs.create(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Phases", "part_number": "#1"},
            run_passed=run_passed,
            phases=[
                Phase(
                    name="Initialization",
                    outcome=PhaseOutcome.PASS,
                    start_time_millis=int((datetime.now() - timedelta(seconds=10)).timestamp() * 1000), #TODO: Should be: start_time=datetime.now() - timedelta(seconds=10),
                    end_time_millis=int(datetime.now().timestamp() * 1000),#TODO: Should be: end_time=datetime.now(),
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

    def test_with_steps(self, client: tofupilot.v2.Client, procedure_identifier, run_passed):
        """Test run creation with deprecated steps parameter."""
        result = client.runs.create(
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

    def test_with_timing(self, client: tofupilot.v2.Client, procedure_identifier, run_passed):
        """Test run creation with timing parameters."""
        start_time = datetime.now() - timedelta(minutes=10)
        end_time = datetime.now()
        
        result = client.runs.create(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Timing", "part_number": "#1"},
            run_passed=run_passed,
            started_at=start_time,
            duration=end_time - start_time,
            ended_at=end_time
        )
        
        assert_create_run_success(result)

    def test_with_metadata(self, client: tofupilot.v2.Client, procedure_identifier, run_passed):
        """Test run creation with metadata parameters."""
        result = client.runs.create(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Metadata", "part_number": "#1"},
            run_passed=run_passed,
            procedure_name="Test Procedure",
            procedure_version="1.0",
            docstring="Comprehensive test with metadata",
            outcome="PASS"
        )
        
        assert_create_run_success(result)

    def test_with_sub_units_and_logs(self, client: tofupilot.v2.Client, procedure_identifier, run_passed):
        """Test run creation with sub-units and logs."""
        result = client.runs.create(
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
                    level="INFO",
                    timestamp="2024-06-30T12:00:00.000Z",
                    source_file=os.path.basename(inspect.getfile(inspect.currentframe())),
                    line_number=inspect.currentframe().f_lineno
                ),
                Log(
                    message="Warning during test",
                    level="WARNING",
                    timestamp="2024-06-30T12:00:05.000Z",
                    source_file=os.path.basename(inspect.getfile(inspect.currentframe())),
                    line_number=inspect.currentframe().f_lineno
                )
            ]
        )
        
        assert_create_run_success(result)

    def test_comprehensive(self, client: tofupilot.v2.Client, procedure_identifier, run_passed):
        """Test run creation with all possible parameters filled."""
        start_time = datetime.now() - timedelta(minutes=5)
        end_time = datetime.now()
        
        result = client.runs.create(
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
                    start_time=start_time,
                    end_time=end_time,
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
            ended_at=end_time,
            outcome="PASS",
            docstring="Full comprehensive test with all parameters",
            sub_units=[SubUnit(serial_number="COMP_SUB001")],
            attachments=[],  # TODO: Add test with actual file paths
            logs=[
                Log(
                    message="Comprehensive test executed",
                    level="INFO",
                    timestamp="2024-06-30T12:00:00.000Z",
                    source_file=os.path.basename(inspect.getfile(inspect.currentframe())),
                    line_number=inspect.currentframe().f_lineno
                )
            ]
        )
        
        assert_create_run_success(result)

    def test_create_and_delete_run(self, client: tofupilot.v2.Client, procedure_identifier, procedure_id):

        initial_runs = client.runs.get(procedureIds=[procedure_id])
        assert_get_runs_success(initial_runs)

        initial_runs = cast(GetRunsResponse, initial_runs)

        serial_number = f"AutomatedTest0002"
        run = client.runs.create(
            procedure_id=procedure_identifier,
            unit_under_test={
                "serial_number": serial_number,
                "part_number": "PCB01"
            },
            run_passed=True,
        )
        assert_create_run_success(run)

        with_new_run = client.runs.get(procedureIds=[procedure_id])
        assert_get_runs_success(with_new_run)

        # Extract run IDs for cleaner comparisons
        initial_run_ids = {run["id"] for run in initial_runs["data"]}
        new_run_ids = {run["id"] for run in with_new_run["data"]}
        created_run_id = run["id"]
        
        assert with_new_run != initial_runs, "Run lists are unchanged"
        assert created_run_id in new_run_ids, f"Created run {created_run_id} not found in updated run list"
        assert created_run_id not in initial_run_ids, f"Run {created_run_id} already existed before creation"

        deletion_result = client.runs.delete(ids=[created_run_id])
        assert_delete_runs_success(deletion_result)

        with_deletion = client.runs.get(procedureIds=[procedure_id])
        assert_get_runs_success(with_deletion)

        deletion_ids = {run["id"] for run in with_deletion["data"]}

        assert deletion_ids != with_new_run, "Run lists are unchanged"
        assert created_run_id not in deletion_ids, f"Run {created_run_id} exists after deletion"

