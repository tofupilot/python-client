"""Test station access control for procedure creation.

This test verifies that the x-access middleware properly rejects procedure creation
requests from stations with the correct HTTP status code and error message.

Based on the OpenAPI x-access definition:
- level: 'unauthorized'
- type: 'station'
- description: 'Stations cannot create procedures'
"""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from ...utils import assert_station_access_forbidden


class TestStationAccessControl:

    def test_station_cannot_create_procedure(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test that stations receive proper HTTP 403 FORBIDDEN error when attempting to create procedures."""
        PROCEDURE_NAME = f"AccessControl-Test-{timestamp}"

        if auth_type == "user":
            result = client.procedures.create(name=PROCEDURE_NAME)
            assert hasattr(result, 'id')
            assert isinstance(result.id, str)
            assert len(result.id) > 0
            return

        with assert_station_access_forbidden("create procedure"):
            client.procedures.create(name=PROCEDURE_NAME)
