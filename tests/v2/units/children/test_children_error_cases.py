"""Tests for error cases when managing unit children."""

import pytest
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from tofupilot.v2 import errors
from ..utils import assert_create_unit_success
from ...utils import assert_station_access_forbidden


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


class TestAddChildrenErrors:
    """Test error cases when adding children to units."""

    def test_add_child_parent_not_found(self, client: TofuPilot, auth_type: str) -> None:
        """Test adding child when parent unit doesn't exist."""
        _, child_serial, _ = create_test_unit(client, "CHILD-ORPHAN")
        
        if auth_type == "station":
            # Stations get 403 Forbidden before 404 Not Found
            with assert_station_access_forbidden("add child with nonexistent parent"):
                client.units.add_child(
                    serial_number="NONEXISTENT-PARENT",
                    child_serial_number=child_serial,
                )
        else:
            # Users get 404 Not Found
            with pytest.raises(errors.ErrorNOTFOUND):
                client.units.add_child(
                    serial_number="NONEXISTENT-PARENT",
                    child_serial_number=child_serial,
                )

    def test_add_child_child_not_found(self, client: TofuPilot, auth_type: str) -> None:
        """Test adding child when child unit doesn't exist."""
        _, parent_serial, _ = create_test_unit(client, "PARENT-NO-CHILD")
        
        if auth_type == "station":
            # Stations get 403 Forbidden before 404 Not Found
            with assert_station_access_forbidden("add nonexistent child"):
                client.units.add_child(
                    serial_number=parent_serial,
                    child_serial_number="NONEXISTENT-CHILD",
                )
        else:
            # Users get 404 Not Found
            with pytest.raises(errors.ErrorNOTFOUND):
                client.units.add_child(
                    serial_number=parent_serial,
                    child_serial_number="NONEXISTENT-CHILD",
                )

    def test_add_child_already_has_parent(self, client: TofuPilot, auth_type: str) -> None:
        """Test adding a child that already has a parent."""
        if auth_type == "station":
            # Stations cannot modify unit relationships at all
            _, parent_serial, _ = create_test_unit(client, "PARENT-STATION")
            child_id, child_serial, _ = create_test_unit(client, "CHILD-STATION")
            
            with assert_station_access_forbidden("add child that already has parent"):
                client.units.add_child(
                    serial_number=parent_serial,
                    child_serial_number=child_serial,
                )
            return
            
        # For users, test the actual error case
        _, parent1_serial, _ = create_test_unit(client, "PARENT1-CONFLICT")
        _, parent2_serial, _ = create_test_unit(client, "PARENT2-CONFLICT")
        child_id, child_serial, _ = create_test_unit(client, "CHILD-CONFLICT")
        
        # Add child to first parent
        client.units.add_child(
            serial_number=parent1_serial,
            child_serial_number=child_serial,
        )
        
        # Try to add the same child to second parent - should fail
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=parent2_serial,
                child_serial_number=child_serial,
            )

    def test_add_child_serial_number_mismatch(self, client: TofuPilot, auth_type: str) -> None:
        """Test when child_serial_number doesn't match the actual child unit's serial number."""
        _, parent_serial, _ = create_test_unit(client, "PARENT-MISMATCH")
        child_id, _, _ = create_test_unit(client, "CHILD-MISMATCH")
        
        if auth_type == "station":
            # Stations get 403 Forbidden before validation errors
            with assert_station_access_forbidden("add child with serial number mismatch"):
                client.units.add_child(
                    serial_number=parent_serial,
                    child_serial_number="WRONG-SERIAL-NUMBER",
                )
        else:
            # Users get proper validation error
            with pytest.raises(errors.ErrorNOTFOUND):
                client.units.add_child(
                    serial_number=parent_serial,
                    child_serial_number="WRONG-SERIAL-NUMBER",
                )


class TestRemoveChildrenErrors:
    """Test error cases when removing children from units."""

    def test_remove_child_parent_not_found(self, client: TofuPilot, auth_type: str) -> None:
        """Test removing child when parent unit doesn't exist."""
        if auth_type == "station":
            # Stations get 403 Forbidden before 404 Not Found
            with assert_station_access_forbidden("remove child with nonexistent parent"):
                client.units.remove_child(
                    serial_number="NONEXISTENT-PARENT",
                    child_serial_number="SOME-CHILD",
                )
        else:
            # Users get 404 Not Found
            with pytest.raises(errors.ErrorNOTFOUND):
                client.units.remove_child(
                    serial_number="NONEXISTENT-PARENT",
                    child_serial_number="SOME-CHILD",
                )

    def test_remove_child_child_not_found(self, client: TofuPilot, auth_type: str) -> None:
        """Test removing child when child unit doesn't exist."""
        _, parent_serial, _ = create_test_unit(client, "PARENT-NO-REMOVE-CHILD")
        
        if auth_type == "station":
            # Stations get 403 Forbidden before 404 Not Found
            with assert_station_access_forbidden("remove nonexistent child"):
                client.units.remove_child(
                    serial_number=parent_serial,
                    child_serial_number="NONEXISTENT-CHILD",
                )
        else:
            # Users get 404 Not Found
            with pytest.raises(errors.ErrorNOTFOUND):
                client.units.remove_child(
                    serial_number=parent_serial,
                    child_serial_number="NONEXISTENT-CHILD",
                )

    def test_remove_child_not_actually_child(self, client: TofuPilot, auth_type: str) -> None:
        """Test removing a unit that is not actually a child of the parent."""
        _, parent_serial, _ = create_test_unit(client, "PARENT-NOT-CHILD")
        unrelated_id, unrelated_serial, _ = create_test_unit(client, "UNRELATED")
        
        if auth_type == "station":
            # Stations get 403 Forbidden before 404 Not Found
            with assert_station_access_forbidden("remove unrelated unit"):
                client.units.remove_child(
                    serial_number=parent_serial,
                    child_serial_number=unrelated_serial,
                )
        else:
            # Users get 404 Not Found
            with pytest.raises(errors.ErrorNOTFOUND):
                client.units.remove_child(
                    serial_number=parent_serial,
                    child_serial_number=unrelated_serial,
                )

    def test_remove_child_serial_number_mismatch(self, client: TofuPilot, auth_type: str) -> None:
        """Test removing child with mismatched serial number."""
        if auth_type == "station":
            # Stations cannot modify unit relationships at all
            _, parent_serial, _ = create_test_unit(client, "PARENT-STATION")
            
            with assert_station_access_forbidden("remove child with serial mismatch"):
                client.units.remove_child(
                    serial_number=parent_serial,
                    child_serial_number="WRONG-SERIAL",
                )
            return
        
        # For users, test the actual error case
        _, parent_serial, _ = create_test_unit(client, "PARENT-REMOVE-MISMATCH")
        child_id, child_serial, _ = create_test_unit(client, "CHILD-REMOVE-MISMATCH")
        
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

    def test_remove_child_from_wrong_parent(self, client: TofuPilot, auth_type: str) -> None:
        """Test removing child using wrong parent serial number."""
        if auth_type == "station":
            # Stations cannot modify unit relationships at all
            _, parent_serial, _ = create_test_unit(client, "PARENT-STATION-WRONG")
            
            with assert_station_access_forbidden("remove child from wrong parent"):
                client.units.remove_child(
                    serial_number=parent_serial,
                    child_serial_number="SOME-CHILD",
                )
            return
            
        # For users, test the actual error case
        _, parent1_serial, _ = create_test_unit(client, "PARENT1-WRONG")
        _, parent2_serial, _ = create_test_unit(client, "PARENT2-WRONG")
        child_id, child_serial, _ = create_test_unit(client, "CHILD-WRONG-PARENT")
        
        # Add child to parent1
        client.units.add_child(
            serial_number=parent1_serial,
            child_serial_number=child_serial,
        )
        
        # Try to remove from parent2 (wrong parent)
        with pytest.raises(errors.ErrorNOTFOUND):
            client.units.remove_child(
                serial_number=parent2_serial,
                child_serial_number=child_serial,
            )