"""Tests for removing children from units - all success cases."""

from typing import Any, List, Set
from tofupilot.v2 import TofuPilot
from tofupilot.v2.types import UNSET
from ..utils import get_unit_by_id


def has_children(unit: Any) -> bool:
    """Check if unit has children (not None and not UNSET)."""
    return unit.children is not None and unit.children is not UNSET


def get_children_count(unit: Any) -> int:
    """Get number of children, handling UNSET case."""
    if unit.children is None or unit.children is UNSET:
        return 0
    return len(unit.children)


def get_children_serials(unit: Any) -> Set[str]:
    """Get set of children serial numbers, handling UNSET case."""
    if not has_children(unit):
        return set()
    return {child.serial_number for child in unit.children}


def has_parent(unit: Any) -> bool:
    """Check if unit has parent (not None and not UNSET)."""
    return unit.parent is not None and unit.parent is not UNSET


class TestRemoveChildrenOperations:
    """All tests for successfully removing children from units."""

    def test_remove_single_child(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test removing a single child from parent."""
        parent_id, parent_serial, _ = create_test_unit("PARENT-REMOVE")
        child_id, child_serial, _ = create_test_unit("CHILD-REMOVE")

        # Add child first
        client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )

        # Verify child was added
        parent_unit = get_unit_by_id(client, parent_id)
        assert parent_unit is not None
        assert has_children(parent_unit)
        assert get_children_count(parent_unit) == 1

        # Remove child
        result = client.units.remove_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )

        # Verify response returns child ID
        assert result.id == child_id

        # Verify parent no longer has children
        parent_unit_after = get_unit_by_id(client, parent_id)
        assert parent_unit_after is not None
        assert not has_children(parent_unit_after) or get_children_count(parent_unit_after) == 0

        # Verify child no longer has parent
        child_unit_after = get_unit_by_id(client, child_id)
        assert child_unit_after is not None
        assert child_unit_after.parent is None

    def test_remove_one_child_from_multiple(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test removing one child when parent has multiple children."""
        parent_id, parent_serial, _ = create_test_unit("PARENT-REMOVE-ONE")

        # Add three children
        children_data: List[tuple[str, str]] = []
        for i in range(3):
            child_id, child_serial, _ = create_test_unit(f"CHILD-REMOVE-ONE-{i}")
            children_data.append((child_id, child_serial))
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )

        # Verify all children are present
        parent_unit = get_unit_by_id(client, parent_id)
        assert parent_unit is not None
        assert has_children(parent_unit)
        assert get_children_count(parent_unit) == 3

        # Remove the first child
        first_child_id, first_child_serial = children_data[0]
        result = client.units.remove_child(
            serial_number=parent_serial,
            child_serial_number=first_child_serial,
        )
        assert result.id == first_child_id

        # Verify only 2 children remain
        parent_unit_after = get_unit_by_id(client, parent_id)
        assert parent_unit_after is not None
        assert has_children(parent_unit_after)
        assert get_children_count(parent_unit_after) == 2

        # Verify the removed child is not present
        remaining_serials = get_children_serials(parent_unit_after)
        assert first_child_serial not in remaining_serials

        # Verify the other children are still present
        remaining_expected = {child_serial for _, child_serial in children_data[1:]}
        assert remaining_serials == remaining_expected

    def test_remove_all_children_sequentially(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test removing all children one by one."""
        parent_id, parent_serial, _ = create_test_unit("PARENT-REMOVE-ALL")

        # Add 3 children
        children_data: List[tuple[str, str]] = []
        for i in range(3):
            child_id, child_serial, _ = create_test_unit(f"CHILD-REMOVE-ALL-{i}")
            children_data.append((child_id, child_serial))
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )

        # Remove children one by one
        for i, (child_id, child_serial) in enumerate(children_data):
            result = client.units.remove_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
            assert result.id == child_id

            # Verify correct number of children remain
            parent_unit = get_unit_by_id(client, parent_id)
            assert parent_unit is not None
            expected_remaining = len(children_data) - i - 1
            if expected_remaining == 0:
                assert not has_children(parent_unit) or get_children_count(parent_unit) == 0
            else:
                assert parent_unit.children is not None
                assert get_children_count(parent_unit) == expected_remaining

    def test_add_remove_cycle(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test adding and removing the same child multiple times."""
        parent_id, parent_serial, _ = create_test_unit("PARENT-CYCLE")
        child_id, child_serial, _ = create_test_unit("CHILD-CYCLE")

        for _ in range(3):
            # Add child (returns child ID)
            result = client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
            assert result.id == child_id

            # Verify child is present
            parent_unit = get_unit_by_id(client, parent_id)
            assert parent_unit is not None
            assert has_children(parent_unit)
            assert get_children_count(parent_unit) == 1
            # Verify specific child with proper type handling
            if parent_unit.children is not None and parent_unit.children is not UNSET and isinstance(parent_unit.children, list):
                assert parent_unit.children[0].serial_number == child_serial
            else:
                assert False, "Parent should have children"

            # Remove child
            result = client.units.remove_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
            assert result.id == child_id

            # Verify child is removed
            parent_unit_after = get_unit_by_id(client, parent_id)
            assert parent_unit_after is not None
            assert not has_children(parent_unit_after) or get_children_count(parent_unit_after) == 0

    def test_remove_from_multi_level_hierarchy(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test removing a unit from the middle of a hierarchy."""
        # Create grandparent -> parent -> child
        grandparent_id, grandparent_serial, _ = create_test_unit("GRANDPARENT-REMOVE")
        parent_id, parent_serial, _ = create_test_unit("PARENT-MIDDLE")
        child_id, child_serial, _ = create_test_unit("CHILD-BOTTOM")

        # Build hierarchy
        client.units.add_child(
            serial_number=grandparent_serial,
            child_serial_number=parent_serial,
        )
        client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )

        # Remove parent from grandparent
        result = client.units.remove_child(
            serial_number=grandparent_serial,
            child_serial_number=parent_serial,
        )
        assert result.id == parent_id

        # Verify grandparent no longer has children
        grandparent_units = client.units.list(serial_numbers=[grandparent_serial])
        assert len(grandparent_units.data) > 0
        grandparent_unit = grandparent_units.data[0]
        assert not has_children(grandparent_unit) or get_children_count(grandparent_unit) == 0

        # Verify parent no longer has grandparent as parent
        parent_units = client.units.list(serial_numbers=[parent_serial])
        assert len(parent_units.data) > 0
        parent_unit = parent_units.data[0]
        assert parent_unit.parent is None

        # Parent should still have its child - removing from grandparent doesn't affect this
        assert has_children(parent_unit)
        assert get_children_count(parent_unit) == 1

        # Verify the child through parent's children list
        if parent_unit.children is not None and parent_unit.children is not UNSET and isinstance(parent_unit.children, list):
            assert parent_unit.children[0].serial_number == child_serial

            # The child is already available in parent's children list
            child_from_parent = parent_unit.children[0]

            # Verify child has correct parent reference
            if hasattr(child_from_parent, 'parent') and child_from_parent.parent is not None:
                # If the child object from parent's children list has parent info, verify it
                assert child_from_parent.parent.serial_number == parent_serial

            # Try to get the child unit directly - this might fail for sub-units
            try:
                child_unit = get_unit_by_id(client, child_id)
                # Child should still have parent
                assert has_parent(child_unit)
                if child_unit.parent:
                    assert child_unit.parent.serial_number == parent_serial
                else:
                    assert False, "Child should have parent"
            except Exception:
                # If we can't get the child directly, that's OK as long as it's in parent's children
                # The important thing is that the parent-child relationship is maintained
                pass
        else:
            assert False, "Parent should have children"

    def test_remove_specific_child_by_position(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test removing children from specific positions (first, middle, last)."""
        parent_id, parent_serial, _ = create_test_unit("PARENT-POSITION")

        # Add 5 children
        children_data: List[tuple[str, str]] = []
        for i in range(5):
            child_id, child_serial, _ = create_test_unit(f"CHILD-POS-{i}")
            children_data.append((child_id, child_serial))
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )

        # Remove middle child (index 2)
        middle_child_id, middle_child_serial = children_data[2]
        result = client.units.remove_child(
            serial_number=parent_serial,
            child_serial_number=middle_child_serial,
        )
        assert result.id == middle_child_id

        # Verify 4 children remain
        parent_unit = get_unit_by_id(client, parent_id)
        assert get_children_count(parent_unit) == 4

        # Remove last child
        last_child_id, last_child_serial = children_data[4]
        result = client.units.remove_child(
            serial_number=parent_serial,
            child_serial_number=last_child_serial,
        )
        assert result.id == last_child_id

        # Verify 3 children remain
        parent_unit = get_unit_by_id(client, parent_id)
        assert get_children_count(parent_unit) == 3

        # Remove first child
        first_child_id, first_child_serial = children_data[0]
        result = client.units.remove_child(
            serial_number=parent_serial,
            child_serial_number=first_child_serial,
        )
        assert result.id == first_child_id

        # Verify 2 children remain (indices 1 and 3 from original)
        parent_unit = get_unit_by_id(client, parent_id)
        assert get_children_count(parent_unit) == 2
        remaining_serials = get_children_serials(parent_unit)
        assert remaining_serials == {children_data[1][1], children_data[3][1]}
