"""Tests for error cases when managing unit children."""

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2 import errors


class TestAddChildrenErrors:
    """Test error cases when adding children to units."""

    def test_add_child_parent_not_found(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test adding child when parent unit doesn't exist."""
        _, child_serial, _ = create_test_unit("CHILD-ORPHAN")

        with pytest.raises(errors.ErrorNOTFOUND):
            client.units.add_child(
                serial_number="NONEXISTENT-PARENT",
                child_serial_number=child_serial,
            )

    def test_add_child_child_not_found(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test adding child when child unit doesn't exist."""
        _, parent_serial, _ = create_test_unit("PARENT-NO-CHILD")

        with pytest.raises(errors.ErrorNOTFOUND):
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number="NONEXISTENT-CHILD",
            )

    def test_add_child_serial_number_mismatch(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test when child_serial_number doesn't match the actual child unit's serial number."""
        _, parent_serial, _ = create_test_unit("PARENT-MISMATCH")
        child_id, _, _ = create_test_unit("CHILD-MISMATCH")

        with pytest.raises(errors.ErrorNOTFOUND):
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number="WRONG-SERIAL-NUMBER",
            )


class TestRemoveChildrenErrors:
    """Test error cases when removing children from units."""

    def test_remove_child_parent_not_found(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test removing child when parent unit doesn't exist."""
        with pytest.raises(errors.ErrorNOTFOUND):
            client.units.remove_child(
                serial_number="NONEXISTENT-PARENT",
                child_serial_number="SOME-CHILD",
            )

    def test_remove_child_child_not_found(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test removing child when child unit doesn't exist."""
        _, parent_serial, _ = create_test_unit("PARENT-NO-REMOVE-CHILD")

        with pytest.raises(errors.ErrorNOTFOUND):
            client.units.remove_child(
                serial_number=parent_serial,
                child_serial_number="NONEXISTENT-CHILD",
            )

    def test_remove_child_not_actually_child(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test removing a unit that is not actually a child of the parent."""
        _, parent_serial, _ = create_test_unit("PARENT-NOT-CHILD")
        unrelated_id, unrelated_serial, _ = create_test_unit("UNRELATED")

        # Units exist but not in parent-child relationship - get 400 Bad Request
        with pytest.raises(errors.ErrorBADREQUEST) as exc_info:
            client.units.remove_child(
                serial_number=parent_serial,
                child_serial_number=unrelated_serial,
            )
        assert "is not a child of" in str(exc_info.value)

    def test_remove_child_serial_number_mismatch(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test removing child with mismatched serial number."""
        _, parent_serial, _ = create_test_unit("PARENT-REMOVE-MISMATCH")
        child_id, child_serial, _ = create_test_unit("CHILD-REMOVE-MISMATCH")

        # Add child first
        client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )

        # Try to remove with wrong serial number
        with pytest.raises(errors.ErrorNOTFOUND):
            client.units.remove_child(
                serial_number=parent_serial,
                child_serial_number="WRONG-SERIAL",
            )

    def test_remove_child_from_wrong_parent(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test removing child using wrong parent serial number."""
        _, parent1_serial, _ = create_test_unit("PARENT1-WRONG")
        _, parent2_serial, _ = create_test_unit("PARENT2-WRONG")
        child_id, child_serial, _ = create_test_unit("CHILD-WRONG-PARENT")

        # Add child to parent1
        client.units.add_child(
            serial_number=parent1_serial,
            child_serial_number=child_serial,
        )

        # Try to remove from parent2 (wrong parent) - units exist but not related
        with pytest.raises(errors.ErrorBADREQUEST) as exc_info:
            client.units.remove_child(
                serial_number=parent2_serial,
                child_serial_number=child_serial,
            )
        assert "is not a child of" in str(exc_info.value)
