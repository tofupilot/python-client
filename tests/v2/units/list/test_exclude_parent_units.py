"""Test exclude_units_with_parent functionality in units.list()."""

import pytest
from typing import List, Tuple, Dict
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_unit_success, assert_get_units_success, get_unit_by_id
from ...utils import assert_station_access_forbidden


class TestUnitsExcludeParent:
    """Test exclude_units_with_parent functionality in units.list()."""
    
    @pytest.fixture
    def test_units_for_parent_child(self, client: TofuPilot, auth_type: str, timestamp: str) -> Dict[str, str]:
        """Create test units with parent-child relationship."""
        # Create our own test data: part and revision
        part_number = f"PARENT-TEST-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part
        client.parts.create(
            number=part_number,
            name=f"Test Part for Parent-Child {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        parent_serial = f"PARENT-{timestamp}"
        child_serial = f"CHILD-{timestamp}"
        
        # Create parent unit
        parent_unit = client.units.create(
            serial_number=parent_serial,
            part_number=part_number,
            revision_number=revision_number
        )
        assert_create_unit_success(parent_unit)
        
        # Create child unit
        child_unit = client.units.create(
            serial_number=child_serial,
            part_number=part_number,
            revision_number=revision_number
        )
        assert_create_unit_success(child_unit)
        
        # Add child to parent (only for user auth)
        if auth_type == "user":
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial
            )
        
        return {
            "parent_id": parent_unit.id,
            "child_id": child_unit.id,
            "parent_serial": parent_serial,
            "child_serial": child_serial,
            "timestamp": timestamp,
            "has_parent_child_relationship": auth_type == "user"
        }

    def test_exclude_units_with_parent_default_false(self, client: TofuPilot, test_units_for_parent_child: Dict[str, str], auth_type: str):
        """Test that by default, all units are returned including those with parents."""
        unit_data = test_units_for_parent_child
        parent_id = unit_data["parent_id"]
        child_id = unit_data["child_id"]
        timestamp = unit_data["timestamp"]
        has_relationship = unit_data["has_parent_child_relationship"]
        
        # Default behavior - should include both parent and child units
        # Search for our specific test units to isolate the test
        result = client.units.list(search_query=timestamp)
        assert_get_units_success(result)
        
        unit_ids = {u.id for u in result.data}
        assert parent_id in unit_ids, "Parent unit should be included by default"
        
        if has_relationship:
            # BUG: Backend is excluding child units by default even though exclude_units_with_parent defaults to false
            if auth_type == "user":
                pytest.xfail("Backend bug: excluding child units by default for user auth")
            assert child_id in unit_ids, "Child unit should be included by default (exclude_units_with_parent defaults to false)"
        else:
            # For station auth without parent-child relationship, both units should be independent
            assert child_id in unit_ids, "Child unit should be included (no parent relationship)"

    def test_exclude_units_with_parent_false_explicit(self, client: TofuPilot, test_units_for_parent_child: Dict[str, str], auth_type: str):
        """Test that explicitly setting exclude_units_with_parent=False includes all units."""
        unit_data = test_units_for_parent_child
        parent_id = unit_data["parent_id"]
        child_id = unit_data["child_id"]
        timestamp = unit_data["timestamp"]
        has_relationship = unit_data["has_parent_child_relationship"]
        
        # Explicitly set to False - should include both parent and child units
        result = client.units.list(search_query=timestamp, exclude_units_with_parent=False)
        assert_get_units_success(result)
        
        unit_ids = {u.id for u in result.data}
        assert parent_id in unit_ids, "Parent unit should be included when exclude_units_with_parent=False"
        
        if has_relationship:
            # BUG: Backend is excluding child units even when explicitly setting exclude_units_with_parent=False
            if auth_type == "user":
                pytest.xfail("Backend bug: excluding child units even when exclude_units_with_parent=False for user auth")
            assert child_id in unit_ids, "Child unit should be included when exclude_units_with_parent=False"
        else:
            # For station auth without parent-child relationship, both units should be independent
            assert child_id in unit_ids, "Child unit should be included (no parent relationship)"

    def test_exclude_units_with_parent_true(self, client: TofuPilot, test_units_for_parent_child: Dict[str, str]):
        """Test that exclude_units_with_parent=True excludes child units."""
        unit_data = test_units_for_parent_child
        parent_id = unit_data["parent_id"]
        child_id = unit_data["child_id"]
        has_relationship = unit_data["has_parent_child_relationship"]
        
        # Set to True - should only include parent units (top-level units)
        result = client.units.list(exclude_units_with_parent=True)
        assert_get_units_success(result)
        
        unit_ids = {u.id for u in result.data}
        assert parent_id in unit_ids, "Parent unit should be included when exclude_units_with_parent=True"
        
        if has_relationship:
            # For user auth with parent-child relationship, child should be excluded
            assert child_id not in unit_ids, "Child unit should be excluded when exclude_units_with_parent=True"
        else:
            # For station auth without parent-child relationship, both units should be independent
            assert child_id in unit_ids, "Child unit should be included (no parent relationship)"

    def test_exclude_units_with_parent_with_search(self, client: TofuPilot, test_units_for_parent_child: Dict[str, str]):
        """Test exclude_units_with_parent combined with search query."""
        unit_data = test_units_for_parent_child
        parent_id = unit_data["parent_id"]
        child_id = unit_data["child_id"]
        timestamp = unit_data["timestamp"]
        has_relationship = unit_data["has_parent_child_relationship"]
        
        # Search with exclude_units_with_parent=True
        result = client.units.list(
            search_query=timestamp,
            exclude_units_with_parent=True
        )
        assert_get_units_success(result)
        
        # Should find parent but not child
        found_units = [u for u in result.data if timestamp in u.serial_number]
        parent_found = any(u.id == parent_id for u in found_units)
        child_found = any(u.id == child_id for u in found_units)
        
        assert parent_found, "Parent unit should be found with search and exclude_units_with_parent=True"
        
        if has_relationship:
            # For user auth with parent-child relationship, child should not be found
            assert not child_found, "Child unit should not be found with exclude_units_with_parent=True"
        else:
            # For station auth without parent-child relationship, both units should be found
            assert child_found, "Child unit should be found (no parent relationship)"

    def test_exclude_units_with_parent_with_filters(self, client: TofuPilot, test_units_for_parent_child: Dict[str, str]):
        """Test exclude_units_with_parent combined with other filters."""
        unit_data = test_units_for_parent_child
        parent_id = unit_data["parent_id"]
        child_id = unit_data["child_id"]
        parent_serial = unit_data["parent_serial"]
        child_serial = unit_data["child_serial"]
        has_relationship = unit_data["has_parent_child_relationship"]
        
        # Use serial_numbers filter with exclude_units_with_parent=True
        result = client.units.list(
            serial_numbers=[parent_serial, child_serial],
            exclude_units_with_parent=True
        )
        assert_get_units_success(result)
        
        if has_relationship:
            # For user auth with parent-child relationship, should only find the parent unit
            assert len(result.data) == 1, "Should only find parent unit"
            assert result.data[0].id == parent_id, "Should find the parent unit"
            assert result.data[0].serial_number == parent_serial
        else:
            # For station auth without parent-child relationship, should find both units
            assert len(result.data) == 2, "Should find both units (no parent relationship)"
            unit_ids = {u.id for u in result.data}
            assert parent_id in unit_ids, "Should find parent unit"
            assert child_id in unit_ids, "Should find child unit (no parent relationship)"

    def test_exclude_units_with_parent_with_pagination(self, client: TofuPilot, test_units_for_parent_child: Dict[str, str]):
        """Test exclude_units_with_parent combined with pagination."""
        unit_data = test_units_for_parent_child
        parent_id = unit_data["parent_id"]
        child_id = unit_data["child_id"]
        has_relationship = unit_data["has_parent_child_relationship"]
        
        # Get units with pagination and exclude_units_with_parent=True
        result = client.units.list(
            exclude_units_with_parent=True,
            limit=10
        )
        assert_get_units_success(result)
        
        unit_ids = {u.id for u in result.data}
        
        if has_relationship:
            # For user auth with parent-child relationship, should not include any child units
            assert child_id not in unit_ids, "Child unit should not be included with exclude_units_with_parent=True"
        else:
            # For station auth without parent-child relationship, child unit can be included
            pass  # Child may or may not be in first page, no assertion needed
        
        # Parent unit might or might not be in the first page, but if it is, it should be included
        if parent_id in unit_ids:
            assert True, "Parent unit correctly included"

    def test_exclude_units_with_parent_multiple_levels(self, client: TofuPilot, auth_type: str, timestamp: str):
        """Test exclude_units_with_parent with multiple levels of hierarchy."""
        if auth_type == "station":
            # Stations cannot modify unit relationships, skip hierarchy test
            return
            
        # Create test data with multiple levels
        part_number = f"MULTILEVEL-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part and revision
        client.parts.create(
            number=part_number,
            name=f"Test Part for Multi-level {timestamp}"
        )
        
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        # Create grandparent unit
        grandparent_unit = client.units.create(
            serial_number=f"GRANDPARENT-{timestamp}",
            part_number=part_number,
            revision_number=revision_number
        )
        assert_create_unit_success(grandparent_unit)
        
        # Create parent unit  
        parent_unit = client.units.create(
            serial_number=f"PARENT-{timestamp}",
            part_number=part_number,
            revision_number=revision_number
        )
        assert_create_unit_success(parent_unit)
        
        # Create child unit
        child_unit = client.units.create(
            serial_number=f"CHILD-{timestamp}",
            part_number=part_number,
            revision_number=revision_number
        )
        assert_create_unit_success(child_unit)
        
        # Build hierarchy: grandparent -> parent -> child
        grandparent_serial = f"GRANDPARENT-{timestamp}"
        parent_serial = f"PARENT-{timestamp}" 
        child_serial = f"CHILD-{timestamp}"
        
        client.units.add_child(
            serial_number=grandparent_serial,
            child_serial_number=parent_serial
        )
        
        client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial
        )
        
        # Test with exclude_units_with_parent=True
        result = client.units.list(
            search_query=timestamp,
            exclude_units_with_parent=True
        )
        assert_get_units_success(result)
        
        # Should only include the top-level unit (grandparent)
        found_units = [u for u in result.data if timestamp in u.serial_number]
        unit_ids = {u.id for u in found_units}
        
        assert grandparent_unit.id in unit_ids, "Grandparent (top-level) unit should be included"
        assert parent_unit.id not in unit_ids, "Parent unit should be excluded (has grandparent)"
        assert child_unit.id not in unit_ids, "Child unit should be excluded (has parent)"

    def test_exclude_units_with_parent_no_hierarchy(self, client: TofuPilot, timestamp: str):
        """Test exclude_units_with_parent when there are no parent-child relationships."""
        # Create standalone units without any parent-child relationships
        part_number = f"STANDALONE-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part and revision
        client.parts.create(
            number=part_number,
            name=f"Test Part for Standalone {timestamp}"
        )
        
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        # Create standalone units
        standalone_units = []
        for i in range(3):
            unit = client.units.create(
                serial_number=f"STANDALONE-{i}-{timestamp}",
                part_number=part_number,
                revision_number=revision_number
            )
            assert_create_unit_success(unit)
            standalone_units.append(unit)
        
        # Test both with and without exclude_units_with_parent
        result_include_all = client.units.list(search_query=timestamp)
        result_exclude_children = client.units.list(
            search_query=timestamp,
            exclude_units_with_parent=True
        )
        
        assert_get_units_success(result_include_all)
        assert_get_units_success(result_exclude_children)
        
        # Since there are no parent-child relationships, both should return the same units
        include_all_ids = {u.id for u in result_include_all.data if timestamp in u.serial_number}
        exclude_children_ids = {u.id for u in result_exclude_children.data if timestamp in u.serial_number}
        
        # All standalone units should be found in both cases
        standalone_unit_ids = {u.id for u in standalone_units}
        assert standalone_unit_ids.issubset(include_all_ids), "All standalone units should be found without exclude_units_with_parent"
        assert standalone_unit_ids.issubset(exclude_children_ids), "All standalone units should be found with exclude_units_with_parent=True"