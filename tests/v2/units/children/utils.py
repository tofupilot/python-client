"""Utility functions for unit children tests."""

from tofupilot.v2 import TofuPilot
from tofupilot.v2.models.unit_addchildop import UnitAddChildResponse
from tofupilot.v2.models.unit_removechildop import UnitRemoveChildResponse
from tofupilot.v2.types import UNSET


def assert_add_child_success(result: UnitAddChildResponse) -> None:
    """Assert that add child response is valid."""
    assert hasattr(result, 'id')
    assert isinstance(result.id, str)
    assert len(result.id) > 0


def assert_remove_child_success(result: UnitRemoveChildResponse) -> None:
    """Assert that remove child response is valid."""
    assert hasattr(result, 'id')
    assert isinstance(result.id, str)
    assert len(result.id) > 0


def verify_parent_child_relationship(
    client: TofuPilot, 
    parent_id: str, 
    child_id: str, 
    expected_child_serial: str
) -> None:
    """Verify that parent-child relationship exists correctly."""
    from ..utils import get_unit_by_id
    
    # Check parent has child
    parent_unit = get_unit_by_id(client, parent_id)
    assert parent_unit is not None
    assert parent_unit.children is not UNSET
    
    if isinstance(parent_unit.children, list):
        child_serials = {child.serial_number for child in parent_unit.children}
        assert expected_child_serial in child_serials
    else:
        assert False, "Children should be a list"
    
    # Check child has parent
    child_unit = get_unit_by_id(client, child_id)
    assert child_unit is not None
    assert child_unit.parent is not None


def verify_no_parent_child_relationship(
    client: TofuPilot, 
    parent_id: str, 
    child_id: str, 
    child_serial: str
) -> None:
    """Verify that parent-child relationship does not exist."""
    from ..utils import get_unit_by_id
    
    # Check parent doesn't have this child
    parent_unit = get_unit_by_id(client, parent_id)
    assert parent_unit is not None
    if parent_unit.children and parent_unit.children is not UNSET:
        child_serials = {child.serial_number for child in parent_unit.children}
        assert child_serial not in child_serials
    
    # Check child doesn't have this parent
    child_unit = get_unit_by_id(client, child_id)
    assert child_unit is not None
    if child_unit.parent:
        assert child_unit.parent.id != parent_id


def count_children(client: TofuPilot, parent_id: str) -> int:
    """Count the number of children for a parent unit."""
    from ..utils import get_unit_by_id
    
    parent_unit = get_unit_by_id(client, parent_id)
    assert parent_unit is not None
    
    children = parent_unit.children
    if children is UNSET or not isinstance(children, list):
        return 0
    return len(children)


def get_child_serials(client: TofuPilot, parent_id: str) -> set[str]:
    """Get set of child serial numbers for a parent unit."""
    from ..utils import get_unit_by_id
    
    parent_unit = get_unit_by_id(client, parent_id)
    assert parent_unit is not None
    
    children = parent_unit.children
    if children is UNSET or not isinstance(children, list):
        return set()
    return {child.serial_number for child in children if hasattr(child, 'serial_number')}