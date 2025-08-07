"""Test that station API properly fails when trying to update parts."""

import time
from tofupilot.v2 import TofuPilot
from ...utils import assert_station_access_forbidden


class TestStationUpdatePermissions:
    """Test station API fails as expected when trying to update parts."""
    
    def test_station_update_fails_as_expected(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that station API cannot update parts."""
        # First create a part to test update
        part_number = f"TEST-STATION-PERM-{timestamp}"
        create_result = client.parts.create(
            number=part_number,
            name="Test Part"
        )
        assert create_result.id is not None
        
        if auth_type == "user":
            # Update should succeed for user
            update_result = client.parts.update(
                number=part_number,
                name="Updated by User"
            )
            assert update_result.id == create_result.id
            assert update_result.name == "Updated by User"
        else:
            # Station should receive HTTP 403 FORBIDDEN when trying to update parts
            # (x-access: unauthorized for station on parts update)
            with assert_station_access_forbidden("update part"):
                client.parts.update(
                    number=part_number,
                    name="Station trying to update"
                )