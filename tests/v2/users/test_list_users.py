"""Test listing users."""

from tofupilot.v2 import TofuPilot
from tofupilot.v2.models import UserListResponse


class TestListUsers:
    """Test user listing functionality."""

    def test_list_all_users(self, client: TofuPilot, auth_type: str) -> None:
        """Test listing all organization users returns a non-empty list with expected fields."""
        result = client.user.list()

        assert isinstance(result, list)
        assert len(result) > 0

        user = result[0]
        assert isinstance(user, UserListResponse)
        assert len(user.id) > 0
        assert len(user.email) > 0
        assert isinstance(user.banned, bool)

    def test_get_current_user(self, client: TofuPilot, auth_type: str) -> None:
        """Test listing with current=True returns only the authenticated user."""
        if auth_type == "station":
            # Stations have no userId, current=True returns empty
            result = client.user.list(current=True)
            assert isinstance(result, list)
            assert len(result) == 0
            return

        result = client.user.list(current=True)

        assert isinstance(result, list)
        assert len(result) == 1

        current_user = result[0]
        assert isinstance(current_user, UserListResponse)
        assert len(current_user.id) > 0
        assert len(current_user.email) > 0
        assert isinstance(current_user.banned, bool)

        # Current user should also appear in the full list
        all_users = client.user.list()
        all_ids = [u.id for u in all_users]
        assert current_user.id in all_ids

