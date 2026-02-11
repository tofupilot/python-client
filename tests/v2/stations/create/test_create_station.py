"""Test creating stations."""

import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorFORBIDDEN
from ..utils import assert_create_station_success, assert_get_station_success


class TestCreateStation:
    """Test creating stations."""

    def test_create_station(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test creating a station with a valid name returns an ID and auto-generated identifier."""
        if auth_type == "station":
            with pytest.raises(ErrorFORBIDDEN):
                client.stations.create(name="Forbidden Station")
            return

        station_name = f"Create Test Station - {timestamp}"
        result = client.stations.create(name=station_name)
        assert_create_station_success(result)

        # Verify via get
        get_result = client.stations.get(id=result.id)
        assert_get_station_success(get_result)
        assert get_result.name == station_name
        assert get_result.identifier.startswith("STA-")

    def test_create_station_with_duplicate_name(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that creating two stations with the same name succeeds (names are not unique)."""
        if auth_type == "station":
            with pytest.raises(ErrorFORBIDDEN):
                client.stations.create(name="Forbidden Station")
            return

        station_name = f"Duplicate Name Station - {timestamp}"
        result1 = client.stations.create(name=station_name)
        assert_create_station_success(result1)

        result2 = client.stations.create(name=station_name)
        assert_create_station_success(result2)

        # Different IDs
        assert result1.id != result2.id

        # Both retrievable with same name
        get1 = client.stations.get(id=result1.id)
        get2 = client.stations.get(id=result2.id)
        assert get1.name == station_name
        assert get2.name == station_name

    def test_create_station_empty_name_fails(self, client: TofuPilot, auth_type: str) -> None:
        """Test that creating a station with an empty name raises a validation error."""
        if auth_type == "station":
            with pytest.raises(ErrorFORBIDDEN):
                client.stations.create(name="")
            return

        with pytest.raises(Exception):
            client.stations.create(name="")
