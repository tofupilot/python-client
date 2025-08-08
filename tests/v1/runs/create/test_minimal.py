"""Test minimal run creation with just required parameters."""

import pytest
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, validate_v1_run_creation, client, v2_client
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

    def test_minimal_run_creation(self, client: TofuPilotClient, v2_client, procedure_identifier, unit_under_test, run_passed):
        """Test minimal run creation with just required parameters."""
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test=unit_under_test,
            run_passed=run_passed,
        )
        
        # Verify successful response
        assert_create_run_success(result)
        
        # Validate the created run using v2 client
        expected_fields = {
            "serial_number": unit_under_test["serial_number"],
            "outcome": run_passed,
        }
        
        # Add optional fields if they're present in the test data
        if "part_number" in unit_under_test:
            expected_fields["part_number"] = unit_under_test["part_number"]
        # part_name is deprecated in v1 API and won't be set
        if "revision" in unit_under_test:
            expected_fields["revision"] = unit_under_test["revision"]
        if "batch_number" in unit_under_test:
            expected_fields["batch_number"] = unit_under_test["batch_number"]
        
        validate_v1_run_creation(v2_client, result["id"], expected_fields)