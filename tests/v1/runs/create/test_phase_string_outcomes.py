"""Test run creation with phase string outcomes."""

import pytest
import time
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, validate_v1_run_creation, client, v2_client
from tofupilot.models.models import Phase


class TestCreateRunPhaseStringOutcomes:
    
    @pytest.fixture(params=[True, False])
    def run_passed(self, request) -> bool:
        return request.param

    def test_run_creation_with_phase_string_outcomes(self, client: TofuPilotClient, v2_client, procedure_identifier, run_passed):
        """Test run creation with phase string outcomes."""
        # Adapted from https://github.com/tofupilot/examples/blob/main/qa/client/create_run/phases_string_outcome/main.py

        def flash_firmware():
            measured_value = "1.2.4" if run_passed else "1.2.0"
            return run_passed, measured_value, None, None, None

        serial_number = "SI0364A1103"

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
        
        # Validate the created run using v2 client
        validate_v1_run_creation(v2_client, result["id"], {
            "serial_number": serial_number,
            "part_number": "SI03645A",
            # part_name is deprecated in v1 API and won't be set
            "revision": "3.1",  # Should be "3.1", not "A"
            "batch_number": "11-24",
            "outcome": passed,
        })