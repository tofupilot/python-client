"""Test updating station details."""

from datetime import datetime, timezone
import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_station_success, assert_update_station_success
from ...utils import assert_station_access_forbidden


class TestUpdateStation:
    """Test updating station details."""

    def test_update_station_name(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating a station's name."""
        if auth_type == "station":
            with assert_station_access_forbidden("update station"):
                client.stations.update(id=str(uuid.uuid4()), name="test")
            return

        original_name = f"Original Station Name - {timestamp}"
        create_result = client.stations.create(name=original_name)
        assert_create_station_success(create_result)
        station_id = create_result.id

        new_name = f"Updated Station Name - {timestamp}"
        update_result = client.stations.update(id=station_id, name=new_name)
        assert_update_station_success(update_result)

        get_result = client.stations.get(id=station_id)
        assert get_result.name == new_name

    def test_update_station_nonexistent(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating a station that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("update nonexistent station"):
                client.stations.update(id=str(uuid.uuid4()), name="New Name")
            return

        with pytest.raises(ErrorNOTFOUND):
            client.stations.update(id=str(uuid.uuid4()), name="New Name")

    def test_update_station_remove_image(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test removing a station's image by passing empty string."""
        if auth_type == "station":
            with assert_station_access_forbidden("update station image"):
                client.stations.update(id=str(uuid.uuid4()), image_id="")
            return

        create_result = client.stations.create(name=f"Station with Image - {timestamp}")
        station_id = create_result.id

        update_result = client.stations.update(id=station_id, image_id="")
        assert_update_station_success(update_result)

    def test_update_station_partial_update(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that unspecified fields remain unchanged during update."""
        if auth_type == "station":
            with assert_station_access_forbidden("update station partial"):
                client.stations.update(id=str(uuid.uuid4()), name="test")
            return

        original_name = f"Partial Update Test - {timestamp}"
        create_result = client.stations.create(name=original_name)
        station_id = create_result.id

        new_name = f"Partially Updated - {timestamp}"
        client.stations.update(id=station_id, name=new_name)

        updated = client.stations.get(id=station_id)
        assert updated.name == new_name

    def test_update_station_unassign_team(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test unassigning a station from its team by passing team_id=None."""
        if auth_type == "station":
            with assert_station_access_forbidden("update station team"):
                client.stations.update(id=str(uuid.uuid4()), name="test")
            return

        create_result = client.stations.create(name=f"Team Unassign Test - {timestamp}")
        station_id = create_result.id

        update_result = client.stations.update(id=station_id, team_id=None)
        assert_update_station_success(update_result)

        get_result = client.stations.get(id=station_id)
        assert get_result.team is None
