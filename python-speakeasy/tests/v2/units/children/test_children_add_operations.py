"""Tests for adding children to units - all success cases."""

from typing import List, Tuple
from tofupilot.v2 import TofuPilot
from ..utils import get_unit_by_id


class TestAddChildrenOperations:
    """All tests for successfully adding children to units."""

    def test_add_single_child(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test adding a single child to a parent unit."""
        parent_id, parent_serial, _ = create_test_unit("PARENT-SINGLE")
        child_id, child_serial, _ = create_test_unit("CHILD-SINGLE")

        # Add child to parent (works for both users and stations)
        result = client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )

        # Verify response returns the child unit ID
        assert result.id == child_id

        # Verify parent-child relationship was established
        parent_unit = get_unit_by_id(client, parent_id)
        assert parent_unit is not None
        assert parent_unit.children is not None
        if parent_unit.children:
            assert len(parent_unit.children) == 1
            assert parent_unit.children[0].serial_number == child_serial

    def test_add_multiple_children_sequentially(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test adding multiple children to one parent sequentially."""
        parent_id, parent_serial, _ = create_test_unit("PARENT-MULTI")

        children_data: List[Tuple[str, str]] = []
        for i in range(3):
            child_id, child_serial, _ = create_test_unit(f"CHILD-MULTI-{i}")
            children_data.append((child_id, child_serial))

            # Add each child - API returns the child unit ID
            result = client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
            assert result.id == child_id

        # Verify all children are present
        parent_unit = get_unit_by_id(client, parent_id)
        assert parent_unit is not None
        assert parent_unit.children is not None
        if parent_unit.children:
            assert len(parent_unit.children) == 3

            # Verify all expected serial numbers are present
            child_serials = {child.serial_number for child in parent_unit.children}
            expected_serials = {child_serial for _, child_serial in children_data}
            assert child_serials == expected_serials

    def test_create_multi_level_hierarchy(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test creating a multi-level parent-child hierarchy."""
        # Create grandparent -> parent -> child
        grandparent_id, grandparent_serial, _ = create_test_unit("GRANDPARENT")
        parent_id, parent_serial, _ = create_test_unit("PARENT")
        child_id, child_serial, _ = create_test_unit("CHILD")

        # Link grandparent -> parent (returns parent_id)
        result1 = client.units.add_child(
            serial_number=grandparent_serial,
            child_serial_number=parent_serial,
        )
        assert result1.id == parent_id

        # Link parent -> child (returns child_id)
        result2 = client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )
        assert result2.id == child_id

        # Verify grandparent has parent as child
        grandparent_unit = get_unit_by_id(client, grandparent_id)
        assert grandparent_unit is not None
        assert grandparent_unit.children is not None
        if grandparent_unit.children:
            assert len(grandparent_unit.children) == 1
            assert grandparent_unit.children[0].serial_number == parent_serial

    def test_create_long_parent_child_chain(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test creating a long parent-child chain (5 levels)."""
        units: List[Tuple[str, str]] = []

        # Create 5 units
        for i in range(5):
            unit_id, unit_serial, _ = create_test_unit(f"CHAIN-{i}")
            units.append((unit_id, unit_serial))

        # Create chain: 0 -> 1 -> 2 -> 3 -> 4
        for i in range(len(units) - 1):
            current_parent_id, current_parent_serial = units[i]
            current_child_id, current_child_serial = units[i + 1]

            result = client.units.add_child(
                serial_number=current_parent_serial,
                child_serial_number=current_child_serial,
            )
            # API returns the child unit ID
            assert result.id == current_child_id

        # Verify the chain was created
        first_unit = get_unit_by_id(client, units[0][0])
        assert first_unit is not None
        assert first_unit.children is not None
        if first_unit.children:
            assert len(first_unit.children) == 1

    def test_add_siblings(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test adding multiple siblings (children with same parent)."""
        parent_id, parent_serial, _ = create_test_unit("PARENT-SIBLINGS")

        # Create and add 5 siblings
        siblings: List[Tuple[str, str]] = []
        for i in range(5):
            sibling_id, sibling_serial, _ = create_test_unit(f"SIBLING-{i}")
            siblings.append((sibling_id, sibling_serial))

            result = client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=sibling_serial,
            )
            # API returns the child (sibling) unit ID
            assert result.id == sibling_id

        # Verify parent has all 5 children
        parent_unit = get_unit_by_id(client, parent_id)
        assert parent_unit is not None
        assert parent_unit.children is not None
        if parent_unit.children:
            assert len(parent_unit.children) == 5

            # Verify all siblings are present
            found_serials = {child.serial_number for child in parent_unit.children}
            expected_serials = {serial for _, serial in siblings}
            assert found_serials == expected_serials
