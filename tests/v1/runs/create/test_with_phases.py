"""Test run creation with phases and measurements."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, client
from tofupilot.models.models import (
    Phase,
    Measurement,
    PhaseOutcome,
    MeasurementOutcome,
)

class TestCreateRunWithPhases:
    
    @pytest.fixture(params=[True, False])
    def run_passed(self, request) -> bool:
        return request.param

    def test_run_creation_with_phases(self, client: TofuPilotClient, procedure_identifier, run_passed):
        """Test run creation with phases and measurements."""
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Phases", "part_number": "Number1"},
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