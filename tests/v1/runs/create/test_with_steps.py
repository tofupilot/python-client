"""Test run creation with deprecated steps parameter."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, client
from tofupilot.models.models import Step


class TestCreateRunWithSteps:
    
    @pytest.fixture(params=[True, False])
    def run_passed(self, request) -> bool:
        return request.param

    def test_run_creation_with_deprecated_steps(self, client: TofuPilotClient, procedure_identifier, run_passed):
        """Test run creation with deprecated steps parameter."""
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Steps", "part_number": "Number1"},
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