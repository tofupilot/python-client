"""Basic integration tests for unit children endpoints."""

import pytest
from datetime import datetime, timezone
from typing import Any, List, Tuple
from tofupilot.v2 import TofuPilot
from tofupilot.v2.types import UNSET
from ..utils import assert_create_unit_success, get_unit_by_id
from ...utils import assert_station_access_forbidden


def has_children(unit: Any) -> bool:
    """Check if unit has children (not UNSET and has items)."""
    return hasattr(unit, 'children') and unit.children is not UNSET and len(unit.children) > 0


def get_children_count(unit: Any) -> int:
    """Get number of children, handling UNSET case."""
    if not has_children(unit):
        return 0
    return len(unit.children)


def has_parent(unit: Any) -> bool:
    """Check if unit has parent (not None and not UNSET)."""
    return hasattr(unit, 'parent') and unit.parent is not None and unit.parent is not UNSET


def create_test_unit(client: TofuPilot, prefix: str) -> tuple[str, str, str]:
    """Create a test unit and return (unit_id, serial_number, revision_id)."""
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    part_number = f"{prefix}-PART-{timestamp}"
    revision_number = f"{prefix}-REV-{timestamp}"
    serial_number = f"{prefix}-{timestamp}"
    
    # Create part and revision
    client.parts.create(
        number=part_number,
        name=f"Test Part {prefix} {timestamp}"
    )
    
    revision_result = client.parts.revisions.create(
        part_number=part_number,
        number=revision_number
    )
    
    # Create unit
    unit_result = client.units.create(
        serial_number=serial_number,
        part_number=part_number,
        revision_number=revision_number,
    )
    
    assert_create_unit_success(unit_result)
    return unit_result.id, serial_number, revision_result.id


class TestUnitChildrenBasicOperations:
    """Basic integration tests combining add and remove operations."""

    def test_complete_add_remove_cycle(self, client: TofuPilot, auth_type: str) -> None:
        """Test complete cycle: create units, add child, verify, remove child, verify."""
        parent_id, parent_serial, _ = create_test_unit(client, "BASIC-PARENT")
        child_id, child_serial, _ = create_test_unit(client, "BASIC-CHILD")
        
        if auth_type == "station":
            # Stations cannot modify unit relationships
            with assert_station_access_forbidden("add child to unit"):
                client.units.add_child(
                    serial_number=parent_serial,
                    child_serial_number=child_serial,
                )
            return
        
        # Test add child endpoint
        add_result = client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )
        
        # Verify the add operation succeeded
        assert add_result.id == parent_id
        
        # Verify parent-child relationship was established
        parent_unit = get_unit_by_id(client, parent_id)
        assert parent_unit is not None
        assert has_children(parent_unit)
        assert get_children_count(parent_unit) == 1
        # Get first child with proper type handling
        if has_children(parent_unit) and isinstance(parent_unit.children, list):
            assert parent_unit.children[0].serial_number == child_serial
        else:
            assert False, "Parent should have children"
        
        # Note: Due to API behavior, child unit is not directly accessible by its original ID
        # after add_child operation. We get the child info from the parent's children list.
        child_from_parent = None
        if has_children(parent_unit) and isinstance(parent_unit.children, list):
            child_from_parent = parent_unit.children[0]
        
        # Test remove child endpoint
        assert child_from_parent is not None, "Should have child from parent"
        remove_result = client.units.remove_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )
        
        # Verify the remove operation succeeded
        assert remove_result.id == child_from_parent.id
        
        # Verify parent-child relationship was removed
        parent_unit_after = get_unit_by_id(client, parent_id)
        assert parent_unit_after is not None
        assert not has_children(parent_unit_after) or get_children_count(parent_unit_after) == 0
        
        # Verify child is restored as independent unit after remove
        child_unit_after = get_unit_by_id(client, child_from_parent.id)
        assert child_unit_after is not None
        assert not has_parent(child_unit_after)

    def test_multiple_operations_sequence(self, client: TofuPilot, auth_type: str) -> None:
        """Test sequence of operations: add multiple, remove one, add another."""
        parent_id, parent_serial, _ = create_test_unit(client, "SEQ-PARENT")
        
        if auth_type == "station":
            # Stations cannot modify unit relationships
            child_id, child_serial, _ = create_test_unit(client, "SEQ-CHILD-STATION")
            with assert_station_access_forbidden("add multiple children to unit"):
                client.units.add_child(
                    serial_number=parent_serial,
                    child_serial_number=child_serial,
                )
            return
        
        # Create and add 3 children
        children: List[Tuple[str, str]] = []
        for i in range(3):
            child_id, child_serial, _ = create_test_unit(client, f"SEQ-CHILD-{i}")
            children.append((child_id, child_serial))
            
            add_result = client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
            assert add_result.id == parent_id
        
        # Verify 3 children
        parent_unit = get_unit_by_id(client, parent_id)
        assert parent_unit is not None
        assert has_children(parent_unit)
        assert get_children_count(parent_unit) == 3
        
        # Remove the middle child - find it from parent's children list
        parent_unit_before_remove = get_unit_by_id(client, parent_id)
        assert parent_unit_before_remove is not None
        assert has_children(parent_unit_before_remove)
        
        # Find the child to remove by serial number
        child_to_remove = None
        if has_children(parent_unit_before_remove) and isinstance(parent_unit_before_remove.children, list):
            for child in parent_unit_before_remove.children:
                if child.serial_number == children[1][1]:  # Middle child serial
                    child_to_remove = child
                    break
        
        assert child_to_remove is not None, "Should find middle child to remove"
        remove_result = client.units.remove_child(
            serial_number=parent_serial,
            child_serial_number=children[1][1],
        )
        assert remove_result.id == child_to_remove.id
        
        # Verify 2 children remain
        parent_unit = get_unit_by_id(client, parent_id)
        assert parent_unit is not None
        assert has_children(parent_unit)
        assert get_children_count(parent_unit) == 2
        
        # Add a new child
        new_child_id, new_child_serial, _ = create_test_unit(client, "SEQ-CHILD-NEW")
        add_result = client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=new_child_serial,
        )
        assert add_result.id == parent_id
        
        # Verify 3 children again
        parent_unit = get_unit_by_id(client, parent_id)
        assert parent_unit is not None
        assert has_children(parent_unit)
        assert get_children_count(parent_unit) == 3
        
        # Verify the expected children are present
        assert parent_unit is not None  # Already checked above
        assert has_children(parent_unit)
        # Get children with proper type handling
        if has_children(parent_unit) and isinstance(parent_unit.children, list):
            child_serials = {child.serial_number for child in parent_unit.children}
            expected_serials = {children[0][1], children[2][1], new_child_serial}
            assert child_serials == expected_serials
        else:
            assert False, "Children should exist at this point"