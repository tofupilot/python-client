"""Test run creation with all possible parameters filled."""

import pytest
import os
import inspect
from datetime import datetime, timedelta
from unittest.mock import patch
from ...utils import client, parentless_unit_serial_number_factory, v2_client

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, validate_v1_run_creation
from tofupilot.models.models import (
    Phase,
    Measurement,
    Log,
    PhaseOutcome,
    MeasurementOutcome,
    LogLevel,
    SubUnit
)

class TestCreateRunAllParameters:
    
    @pytest.fixture(params=[True, False])
    def run_passed(self, request) -> bool:
        return request.param

    def test_run_creation_with_all_possible_parameters(self, client: TofuPilotClient, v2_client, procedure_identifier, parentless_unit_serial_number_factory, run_passed):
        """Test run creation with all possible parameters filled."""
        start_time = datetime.now() - timedelta(minutes=5)
        end_time = datetime.now()
        
        # Define test data
        unit_data = {
            "serial_number": "AutomatedTest_AllParameters",
            "part_number": "Number1",
            "part_name": "All Parameters Test Unit",
            "revision": "2.0",
            "batch_number": "BATCH001"
        }
        procedure_version = "2.1.0"
        
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test=unit_data,
            run_passed=run_passed,
            procedure_name="All Parameters Test Procedure",
            procedure_version=procedure_version,
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
            sub_units=[SubUnit(serial_number=parentless_unit_serial_number_factory())],
            attachments=[
                "tests/v1/attachments/temperature-map.png",
                "tests/v1/attachments/performance-report.pdf",
            ],
            logs=[
                Log(
                    message="All parameters test executed",
                    level=LogLevel.INFO,
                    timestamp="2024-06-30T12:00:00.000Z",
                    source_file=os.path.basename(inspect.getfile(inspect.currentframe())),
                    line_number=inspect.currentframe().f_lineno
                )
            ]
        )
        
        assert_create_run_success(result)
        
        # Validate the created run using v2 client
        validate_v1_run_creation(v2_client, result["id"], {
            "serial_number": unit_data["serial_number"],
            "part_number": unit_data["part_number"],
            # part_name is deprecated in v1 API and won't be set
            "revision": unit_data["revision"],  # This should be "2.0", not "A"
            "batch_number": unit_data["batch_number"],
            "outcome": run_passed,
            "procedure_version": procedure_version
        })