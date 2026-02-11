"""Test getting the current authenticated station."""

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.models import StationGetCurrentResponse
from tofupilot.v2.errors import ErrorFORBIDDEN
from trycast import checkcast


class TestGetCurrentStation:
    """Test getting the current authenticated station."""

    def test_get_current_station_with_station_auth(self, client: TofuPilot, auth_type: str) -> None:
        """Test that a station-authenticated client can retrieve its own station info."""
        if auth_type == "user":
            with pytest.raises(ErrorFORBIDDEN):
                client.stations.get_current()
            return

        result = client.stations.get_current()
        assert checkcast(StationGetCurrentResponse, result)
        assert len(result.id) > 0
        assert len(result.identifier) > 0
        assert len(result.name) > 0
        assert isinstance(result.procedures, list)
        assert result.connection_status is None or result.connection_status in ["connected", "disconnected"]

    def test_get_current_station_user_auth_forbidden(self, client: TofuPilot, auth_type: str) -> None:
        """Test that a user-authenticated client gets 403 when calling get_current."""
        if auth_type == "station":
            # Station auth succeeds for get_current — tested above
            result = client.stations.get_current()
            assert checkcast(StationGetCurrentResponse, result)
            return

        with pytest.raises(ErrorFORBIDDEN):
            client.stations.get_current()
