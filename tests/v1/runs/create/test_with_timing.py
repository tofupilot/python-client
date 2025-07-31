"""Test run creation with timing parameters."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, client


class TestCreateRunWithTiming:
    
    @pytest.fixture(params=[True, False])
    def run_passed(self, request) -> bool:
        return request.param

    def test_run_creation_with_timing_parameters(self, client: TofuPilotClient, procedure_identifier, run_passed):
        """Test run creation with timing parameters."""
        start_time = datetime.now() - timedelta(minutes=10)
        end_time = datetime.now()
        
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_Timing", "part_number": "Number1"},
            run_passed=run_passed,
            started_at=start_time,
            duration=end_time - start_time,
        )
        
        assert_create_run_success(result)