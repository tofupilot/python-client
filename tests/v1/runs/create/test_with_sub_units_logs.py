"""Test run creation with sub-units and logs."""

import pytest
import os
import inspect
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, client, parentless_unit_serial_number_factory
from tofupilot.models.models import (
    Log,
    LogLevel,
    SubUnit
)


class TestCreateRunWithSubUnitsAndLogs:
    
    @pytest.fixture(params=[True, False])
    def run_passed(self, request) -> bool:
        return request.param

    def test_run_creation_with_sub_units_and_logs(self, client: TofuPilotClient, procedure_identifier, parentless_unit_serial_number_factory, run_passed):
        """Test run creation with sub-units and logs."""

        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "AutomatedTest_SubLogs", "part_number": "Number1"},
            run_passed=run_passed,
            sub_units=[
                SubUnit(
                    serial_number=parentless_unit_serial_number_factory()
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