"""Test basic unit listing functionality."""

from tofupilot.v2 import TofuPilot
from ...utils import assert_get_units_success


class TestGetUnitsBasic:

    def test_list_all_units_no_parameters(self, client: TofuPilot):
        """Test getting all units with no filters."""
        result = client.units.list()
        assert_get_units_success(result)

    def test_list_units_with_limit(self, client: TofuPilot):
        """Test pagination using limit parameter."""
        result = client.units.list(limit=5)
        assert_get_units_success(result)
        assert len(result.data) <= 5