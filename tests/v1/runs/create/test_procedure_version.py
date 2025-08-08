"""Test run creation with procedure versioning."""

import pytest
import time
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, validate_v1_run_creation, client, v2_client


class TestCreateRunProcedureVersion:
    
    @pytest.fixture(params=[3, 3.1, 3.9, 4])
    def voltage(self, request) -> bool:
        return request.param

    def test_run_creation_with_procedure_version(self, client: TofuPilotClient, v2_client, procedure_identifier, voltage):
        """Test run creation with procedure versioning."""
        # adapted from https://github.com/tofupilot/examples/blob/5cf044d0e55c11ea55114014edb206605689aa6d/qa/client/create_run/procedure_version/main.py
        
        # Generate SN
        serial_number = "SI0364A084561"

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
        
        # Validate the created run using v2 client
        validate_v1_run_creation(v2_client, result["id"], {
            "serial_number": serial_number,
            "part_number": "SI0364",
            "revision": "A",  # This test expects "A"
            "outcome": passed,
            "procedure_version": "1.2.20",
        })