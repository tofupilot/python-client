"""Tests for cycle detection in unit parent-child relationships."""

import pytest
from tofupilot.v2 import TofuPilot, errors


class TestCycleDetection:
    """Tests to ensure cycles cannot be created in parent-child relationships."""

    def test_self_reference_prevention(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test that a unit cannot be its own child (direct cycle)."""
        unit_id, unit_serial, _ = create_test_unit("SELF-REFERENCE")

        with pytest.raises(errors.ErrorBADREQUEST):
            client.units.add_child(
                serial_number=unit_serial,
                child_serial_number=unit_serial,
            )

    def test_two_level_cycle_prevention(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test preventing 2-level cycle: A -> B, then B -> A."""
        unit_a_id, unit_a_serial, _ = create_test_unit("CYCLE-2-A")
        unit_b_id, unit_b_serial, _ = create_test_unit("CYCLE-2-B")

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

    def test_three_level_cycle_prevention(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test preventing 3-level cycle: A -> B -> C, then C -> A."""
        unit_a_id, unit_a_serial, _ = create_test_unit("CYCLE-3-A")
        unit_b_id, unit_b_serial, _ = create_test_unit("CYCLE-3-B")
        unit_c_id, unit_c_serial, _ = create_test_unit("CYCLE-3-C")

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

    def test_four_level_cycle_prevention(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test preventing 4-level cycle: A -> B -> C -> D, then D -> A."""
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

    def test_deep_cycle_prevention(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test preventing cycle in a deep hierarchy (10 levels)."""
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

    def test_multiple_children_no_cycle(
        self, client: TofuPilot, auth_type: str, create_test_unit
    ) -> None:
        """Test that having multiple children doesn't prevent valid operations."""
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
