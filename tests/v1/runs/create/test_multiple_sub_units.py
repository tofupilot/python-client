"""Test run creation with multiple sub-units."""

import pytest
from unittest.mock import patch

from tofupilot.client import TofuPilotClient
from ...utils import assert_create_run_success, client, parentless_unit_serial_number_factory


class TestCreateRunMultipleSubUnits:

    def test_run_creation_with_multiple_sub_units(self, client: TofuPilotClient, procedure_identifier, parentless_unit_serial_number_factory):
        """Test run creation with multiple sub-units."""
        
        sn1 = parentless_unit_serial_number_factory()
        sn2 = parentless_unit_serial_number_factory()

        assert sn1 != sn2

        # Adapted from https://github.com/tofupilot/examples/blob/5cf044d0e55c11ea55114014edb206605689aa6d/qa/client/create_run/multiple_sub_units/main.py
        result = client.create_run(
            procedure_id=procedure_identifier,
            unit_under_test={"serial_number": "00003", "part_number": "SI002"},
            run_passed=True,
            sub_units=[{"serial_number": sn1}, {"serial_number": sn2}],
        )
        assert_create_run_success(result)