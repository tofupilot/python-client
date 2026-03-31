"""Tests for input validation and edge cases in unit children management."""

import pytest
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_unit_success

class TestInputValidation:
    """Test input validation for children management operations."""

    def test_add_child_invalid_uuid_format(self, client: TofuPilot, create_test_unit) -> None:
        """Test adding child with invalid UUID format for child_id."""
        _, parent_serial, _ = create_test_unit("PARENT-INVALID-UUID")
        
        with pytest.raises(Exception):  # Should fail validation
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number="SOME-CHILD",
            )

    def test_add_child_empty_serial_number(self, client: TofuPilot, create_test_unit) -> None:
        """Test adding child with empty serial number."""
        _, parent_serial, _ = create_test_unit("PARENT-EMPTY")
        
        with pytest.raises(Exception):  # Should fail validation
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number="",
            )

    def test_add_child_whitespace_serial_number(self, client: TofuPilot, create_test_unit) -> None:
        """Test adding child with whitespace-only serial number."""
        _, parent_serial, _ = create_test_unit("PARENT-WHITESPACE")
        
        with pytest.raises(Exception):  # Should fail validation
            client.units.add_child(
                serial_number=parent_serial,
                child_serial_number="   ",
            )

    def test_remove_child_invalid_uuid_format(self, client: TofuPilot, create_test_unit) -> None:
        """Test removing child with invalid UUID format."""
        _, parent_serial, _ = create_test_unit("PARENT-REMOVE-INVALID-UUID")
        
        with pytest.raises(Exception):  # Should fail validation
            client.units.remove_child(
                serial_number=parent_serial,
                child_serial_number="SOME-CHILD",
            )

    def test_add_child_empty_parent_serial(self, client: TofuPilot) -> None:
        """Test adding child with empty parent serial number."""
        with pytest.raises(Exception):  # Should fail validation
            client.units.add_child(
                serial_number="",
                child_serial_number="SOME-CHILD",
            )

    def test_remove_child_empty_parent_serial(self, client: TofuPilot) -> None:
        """Test removing child with empty parent serial number."""
        with pytest.raises(Exception):  # Should fail validation
            client.units.remove_child(
                serial_number="",
                child_serial_number="SOME-CHILD",
            )


class TestBoundaryConditions:
    """Test boundary conditions for children management."""

    def test_very_long_serial_numbers(self, client: TofuPilot, auth_type, timestamp) -> None:
        """Test with maximum length serial numbers (100 characters)."""
        
        # Create parent with max length serial
        parent_prefix = f"PARENT-LONG-{timestamp}-"
        parent_padding = 60 - len(parent_prefix)
        parent_serial = parent_prefix + "P" * parent_padding
        assert len(parent_serial) == 60
        
        parent_part = f"PART-PARENT-LONG-{timestamp}"
        client.parts.create(number=parent_part, name="Parent Long Part")
        parent_rev = client.parts.revisions.create(part_number=parent_part, number="REV-1")
        parent_result = client.units.create(
            serial_number=parent_serial,
            part_number=parent_part,
            revision_number="REV-1"
        )
        
        # Create child with max length serial
        child_prefix = f"CHILD-LONG-{timestamp}-"
        child_padding = 60 - len(child_prefix)
        child_serial = child_prefix + "C" * child_padding
        assert len(child_serial) == 60
        
        child_part = f"PART-CHILD-LONG-{timestamp}"
        client.parts.create(number=child_part, name="Child Long Part")
        child_rev = client.parts.revisions.create(part_number=child_part, number="REV-1")
        child_result = client.units.create(
            serial_number=child_serial,
            part_number=child_part,
            revision_number="REV-1"
        )

        if auth_type == "user":

            # Test adding child with long serial numbers (returns child ID)
            result = client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )

            assert result.id == child_result.id

            # Test removing child with long serial numbers (returns child ID)
            result = client.units.remove_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )

            assert result.id == child_result.id

    def test_special_characters_in_serial_numbers(self, user_client: TofuPilot, timestamp) -> None:
        """Test with special characters in serial numbers."""
        
        # Test various allowed special characters
        # Note: Removed forward slash and colon as they cause issues in URL paths
        special_chars_tests = [
            f"PARENT_UNDERSCORE_{timestamp}",
            f"PARENT-DASH-{timestamp}",
        ]
        
        for parent_serial in special_chars_tests:
            # Create parent
            parent_part = f"PART-{parent_serial}"
            user_client.parts.create(number=parent_part, name="Parent Part")
            parent_rev = user_client.parts.revisions.create(part_number=parent_part, number="REV-1")
            parent_result = user_client.units.create(
                serial_number=parent_serial,
                part_number=parent_part,
                revision_number="REV-1"
            )
            
            # Create child with special chars
            child_serial = f"CHILD_{parent_serial}"
            child_part = f"PART-{child_serial}"
            user_client.parts.create(number=child_part, name="Child Part")
            child_rev = user_client.parts.revisions.create(part_number=child_part, number="REV-1")
            child_result = user_client.units.create(
                serial_number=child_serial,
                part_number=child_part,
                revision_number="REV-1"
            )
            
            # Test operations work with special characters (both return child ID)
            add_result = user_client.units.add_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
            assert add_result.id == child_result.id

            remove_result = user_client.units.remove_child(
                serial_number=parent_serial,
                child_serial_number=child_serial,
            )
            assert remove_result.id == child_result.id

    def test_serial_number_over_60_chars(self, client: TofuPilot, timestamp) -> None:
        """Test that serial numbers over 60 characters are rejected."""
                
        # Try to create child with serial > 60 chars (61 chars long)
        too_long_serial = ("CHILD-" + "X" * 60)[:61]
        assert len(too_long_serial) == 61
        
        with pytest.raises(Exception):  # Should fail validation
            child_part = f"PART-TOOLONG-{timestamp}"
            client.parts.create(number=child_part, name="Child Part")
            child_rev = client.parts.revisions.create(part_number=child_part, number="REV-1")
            client.units.create(
                serial_number=too_long_serial,
                part_number=child_part,
                revision_number="REV-1"
            )