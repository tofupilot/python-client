"""Tests for cycle detection in unit parent-child relationships."""

import pytest
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from tofupilot.v2 import errors
from ..utils import assert_create_unit_success
from ...utils import assert_station_access_forbidden

class TestCycleDetection:
    """Tests to ensure cycles cannot be created in parent-child relationships."""

    def test_self_reference_prevention(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test that a unit cannot be its own child (direct cycle)."""
        unit_id, unit_serial, _ = create_test_unit("SELF-REFERENCE")
        
        if auth_type == "station":
            # Stations cannot modify unit relationships
            with assert_station_access_forbidden("add child for self-reference prevention test"):
                client.units.add_child(
                    serial_number=unit_serial,
                    child_serial_number=unit_serial,
                )
            return
        
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=unit_serial,
                child_serial_number=unit_serial,
            )

    def test_two_level_cycle_prevention(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test preventing 2-level cycle: A -> B, then B -> A."""
        unit_a_id, unit_a_serial, _ = create_test_unit("CYCLE-2-A")
        unit_b_id, unit_b_serial, _ = create_test_unit("CYCLE-2-B")
        
        if auth_type == "station":
            # Stations cannot modify unit relationships - verify 403 on first operation
            with assert_station_access_forbidden("add child for cycle prevention test"):
                client.units.add_child(
                    serial_number=unit_a_serial,
                    child_serial_number=unit_b_serial,
                )
            return
        
        # Create A -> B
        client.units.add_child(
            serial_number=unit_a_serial,
            child_serial_number=unit_b_serial,
        )
        
        # Try to create B -> A (should fail)
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=unit_b_serial,
                child_serial_number=unit_a_serial,
            )

    def test_three_level_cycle_prevention(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test preventing 3-level cycle: A -> B -> C, then C -> A."""
        unit_a_id, unit_a_serial, _ = create_test_unit("CYCLE-3-A")
        unit_b_id, unit_b_serial, _ = create_test_unit("CYCLE-3-B")
        unit_c_id, unit_c_serial, _ = create_test_unit("CYCLE-3-C")
        
        if auth_type == "station":
            # Stations cannot modify unit relationships - verify 403 on first operation
            with assert_station_access_forbidden("add child for 3-level cycle test"):
                client.units.add_child(
                    serial_number=unit_a_serial,
                    child_serial_number=unit_b_serial,
                )
            return
        
        # Create chain: A -> B -> C
        client.units.add_child(
            serial_number=unit_a_serial,
            child_serial_number=unit_b_serial,
        )
        
        client.units.add_child(
            serial_number=unit_b_serial,
            child_serial_number=unit_c_serial,
        )
        
        # Try to create cycle: C -> A (should fail)
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=unit_c_serial,
                child_serial_number=unit_a_serial,
            )

    def test_four_level_cycle_prevention(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test preventing 4-level cycle: A -> B -> C -> D, then D -> A."""
        if auth_type == "station":
            # Stations cannot modify unit relationships
            unit_a_id, unit_a_serial, _ = create_test_unit("CYCLE-4-A-STATION")
            unit_b_id, unit_b_serial, _ = create_test_unit("CYCLE-4-B-STATION")
            with assert_station_access_forbidden("add child for 4-level cycle test"):
                client.units.add_child(
                    serial_number=unit_a_serial,
                    child_serial_number=unit_b_serial,
                )
            return
            
        units: list[tuple[str, str]] = []
        for i in range(4):
            unit_id, unit_serial, _ = create_test_unit(f"CYCLE-4-{chr(65+i)}")
            units.append((unit_id, unit_serial))
        
        # Create chain: A -> B -> C -> D
        for i in range(len(units) - 1):
            _, parent_serial = units[i]
            child_id, child_serial = units[i + 1]
            
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
        
        # Try to create cycle: D -> A (should fail)
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=units[3][1],  # D
                child_serial_number=units[0][1],
            )

    def test_deep_cycle_prevention(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test preventing cycle in a deep hierarchy (10 levels)."""
        if auth_type == "station":
            # Stations cannot modify unit relationships
            unit_a_id, unit_a_serial, _ = create_test_unit("DEEP-A-STATION")
            unit_b_id, unit_b_serial, _ = create_test_unit("DEEP-B-STATION")
            with assert_station_access_forbidden("add child for deep cycle test"):
                client.units.add_child(
                    serial_number=unit_a_serial,
                    child_serial_number=unit_b_serial,
                )
            return
            
        units: list[tuple[str, str]] = []
        for i in range(10):
            unit_id, unit_serial, _ = create_test_unit(f"DEEP-{i}")
            units.append((unit_id, unit_serial))
        
        # Create deep chain: 0 -> 1 -> 2 -> ... -> 9
        for i in range(len(units) - 1):
            _, parent_serial = units[i]
            child_id, child_serial = units[i + 1]
            
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
        
        # Try to create cycle at any level (test a few)
        # Try 9 -> 0 (full cycle)
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=units[9][1],
                child_serial_number=units[0][1],
            )
        
        # Try 9 -> 5 (partial cycle)
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=units[9][1],
                child_serial_number=units[5][1],
            )
        
        # Try 5 -> 2 (mid-chain cycle)
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=units[5][1],
                child_serial_number=units[2][1],
            )

    def test_diamond_pattern_prevention(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test preventing diamond pattern that would create a cycle."""
        if auth_type == "station":
            # Stations cannot modify unit relationships
            unit_a_id, unit_a_serial, _ = create_test_unit("DIAMOND-A-STATION")
            unit_b_id, unit_b_serial, _ = create_test_unit("DIAMOND-B-STATION")
            with assert_station_access_forbidden("add child for diamond pattern test"):
                client.units.add_child(
                    serial_number=unit_a_serial,
                    child_serial_number=unit_b_serial,
                )
            return
            
        # Create units: A, B, C, D
        unit_a_id, unit_a_serial, _ = create_test_unit("DIAMOND-A")
        unit_b_id, unit_b_serial, _ = create_test_unit("DIAMOND-B")
        unit_c_id, unit_c_serial, _ = create_test_unit("DIAMOND-C")
        unit_d_id, unit_d_serial, _ = create_test_unit("DIAMOND-D")
        
        # Create structure:
        # A -> B
        # A -> C  
        # B -> D
        # Then try: C -> D (would create diamond, which is OK)
        # Then try: D -> A (would create cycle, which is NOT OK)
        
        # A -> B
        client.units.add_child(
            serial_number=unit_a_serial,
            child_serial_number=unit_b_serial,
        )
        
        # A -> C
        client.units.add_child(
            serial_number=unit_a_serial,
            child_serial_number=unit_c_serial,
        )
        
        # B -> D
        client.units.add_child(
            serial_number=unit_b_serial,
            child_serial_number=unit_d_serial,
        )
        
        # C -> D would create a diamond but NOT a cycle
        # This should fail because D already has parent B
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=unit_c_serial,
                child_serial_number=unit_d_serial,
            )
        
        # D -> A would create a cycle (should fail)
        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=unit_d_serial,
                child_serial_number=unit_a_serial,
            )

    def test_multiple_children_no_cycle(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test that having multiple children doesn't prevent valid operations."""
        if auth_type == "station":
            # Stations cannot modify unit relationships
            parent_id, parent_serial, _ = create_test_unit("MULTI-PARENT-STATION")
            child_id, child_serial, _ = create_test_unit("MULTI-CHILD-STATION")
            with assert_station_access_forbidden("add child for multiple children test"):
                client.units.add_child(
                    serial_number=parent_serial,
                    child_serial_number=child_serial,
                )
            return
            
        # Create parent with multiple children (tree structure)
        parent_id, parent_serial, _ = create_test_unit("TREE-PARENT")
        
        # Add 3 children
        children: list[tuple[str, str]] = []
        for i in range(3):
            child_id, child_serial, _ = create_test_unit(f"TREE-CHILD-{i}")
            children.append((child_id, child_serial))
            
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
        
        # Each child can have their own children (no cycles)
        grandchildren: list[tuple[str, str]] = []
        for i, (child_id, child_serial) in enumerate(children):
            grandchild_id, grandchild_serial, _ = create_test_unit(f"TREE-GRANDCHILD-{i}")
            grandchildren.append((grandchild_id, grandchild_serial))
            
            # This should work fine (no cycle)
            client.units.add_child(
                serial_number=child_serial,
                child_serial_number=grandchild_serial,
            )
        
        # But grandchildren cannot be added back to parent or grandparent
        for grandchild_id, grandchild_serial in grandchildren:
            # Grandchild -> Parent (skip level cycle)
            with pytest.raises(errors.ErrorBADREQUEST):
                client.units.add_child(
                    serial_number=grandchild_serial,
                    child_serial_number=parent_serial,
                )