"""Test run creation with file attachments."""

import pytest
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, client


class TestCreateRunWithAttachments:

    def test_run_creation_with_file_attachments(self, client: TofuPilotClient, procedure_identifier):
        """Test run creation with file attachments."""
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
            run_passed=True,
            attachments=[
                "tests/v1/attachments/temperature-map.png",
                "tests/v1/attachments/performance-report.pdf",
            ],
        )
        assert_create_run_success(result)