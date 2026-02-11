"""Test deleting units."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_delete_unit_success, assert_get_unit_success
from ...utils import assert_station_access_forbidden


class TestDeleteUnit:
    """Test deleting units."""

    def test_delete_unit_by_serial_number(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test deleting a unit and verifying it's gone."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete unit"):
                client.units.delete(serial_numbers=["any"])
            return

        unit_id, serial, _ = create_test_unit("DEL-UNIT")

        result = client.units.delete(serial_numbers=[serial])
        assert_delete_unit_success(result)
        assert unit_id in result.ids

        with pytest.raises(ErrorNOTFOUND):
            client.units.get(serial_number=serial)

    def test_delete_nonexistent_unit(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting a unit that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete nonexistent unit"):
                client.units.delete(serial_numbers=["nonexistent"])
            return

        fake_serial = f"NONEXISTENT-{uuid.uuid4().hex[:8]}"

        with pytest.raises(ErrorNOTFOUND):
            client.units.delete(serial_numbers=[fake_serial])

    def test_delete_unit_with_children(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test deleting a parent unit and verifying child behavior."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete unit with children"):
                client.units.delete(serial_numbers=["any"])
            return

        parent_id, parent_serial, _ = create_test_unit("DEL-PAR-P")
        child_id, child_serial, _ = create_test_unit("DEL-PAR-C")

        client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )

        # Delete the parent
        result = client.units.delete(serial_numbers=[parent_serial])
        assert_delete_unit_success(result)

        # Parent should be gone
        with pytest.raises(ErrorNOTFOUND):
            client.units.get(serial_number=parent_serial)

        # Child should still exist without a parent
        child = client.units.get(serial_number=child_serial)
        assert_get_unit_success(child)
        assert child.id == child_id
        assert child.parent is None
