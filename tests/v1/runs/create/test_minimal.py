"""Test minimal run creation with just required parameters."""

import pytest
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, client
from tofupilot.models.models import UnitUnderTest


class TestCreateRunMinimal:
    
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
            "part_number": "Number1",
            **request.param  # pyright: ignore[reportReturnType]
        }
    
    @pytest.fixture(params=[True, False])
    def run_passed(self, request) -> bool:
        return request.param

    def test_minimal_run_creation(self, client: TofuPilotClient, procedure_identifier, unit_under_test, run_passed):
        """Test minimal run creation with just required parameters."""
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test=unit_under_test,
            run_passed=run_passed,
        )
        
        # Verify successful response
        assert_create_run_success(result)