"""Test parts update validation rules."""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError, ErrorCONFLICT, ErrorNOTFOUND
from ..utils import assert_create_part_success
from ...utils import assert_station_access_limited


class TestUpdatePartValidation:
    """Test parts update validation scenarios."""
    
    def test_update_nonexistent_part(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating a part that doesn't exist."""
        fake_number = "NONEXISTENT-PART-12345"
        
        if auth_type == "station":
            # Station has limited access to update parts
            with assert_station_access_limited("update nonexistent part"):
                client.parts.update(
                    number=fake_number,
                    name="New Name"
                )
        else:
            # User should get NOT_FOUND error
            with pytest.raises(ErrorNOTFOUND) as exc_info:
                client.parts.update(
                    number=fake_number,
                    name="New Name"
                )
            
            error_message = str(exc_info.value).lower()
            assert "not found" in error_message or "does not exist" in error_message
    
    def test_update_invalid_number_format(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating with empty number — resolves to a non-existent route."""
        with pytest.raises(ErrorNOTFOUND):
            client.parts.update(
                number="",
                name="New Name"
            )
    
    def test_update_duplicate_part_number(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating to a part number that already exists."""
        
        # Create two parts
        part1_number = f"PART1-{timestamp}"
        part2_number = f"PART2-{timestamp}"
        
        part1 = client.parts.create(number=part1_number)
        assert_create_part_success(part1)
        
        part2 = client.parts.create(number=part2_number)
        assert_create_part_success(part2)
        
        # Try to update part2 to have part1's number
        if auth_type == "station":
            # Station has limited access to update parts
            with assert_station_access_limited("update part to duplicate number"):
                client.parts.update(
                    number=part2_number,
                    new_number=part1_number
                )
        else:
            # User should get CONFLICT error
            with pytest.raises(ErrorCONFLICT) as exc_info:
                client.parts.update(
                    number=part2_number,
                    new_number=part1_number
                )
            
            error_message = str(exc_info.value).lower()
            assert "already exists" in error_message or "conflict" in error_message or "duplicate" in error_message
    
    def test_update_empty_part_number(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part with empty number."""
        
        # Create a part
        part_number = f"PART-{timestamp}"
        part = client.parts.create(number=part_number)
        assert_create_part_success(part)
        
        # Try to update with empty number
        from tofupilot.v2.errors import ErrorBADREQUEST
        
        # Both user and station should fail with empty number
        with pytest.raises((APIError, ErrorBADREQUEST)) as exc_info:
            client.parts.update(
                number=part_number,
                new_number=""
            )
        
        if auth_type == "user":
            error_message = str(exc_info.value).lower()
            assert "validation" in error_message or "invalid" in error_message or "empty" in error_message
    
    def test_update_part_number_too_long(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part with number > 60 chars."""
        
        # Create a part
        part_number = f"PART-{timestamp}"
        part = client.parts.create(number=part_number)
        assert_create_part_success(part)
        
        # Try to update with long number (> 60 chars)
        long_number = "X" * 61
        from tofupilot.v2.errors import ErrorBADREQUEST
        
        # Both user and station should fail with long number
        with pytest.raises((APIError, ErrorBADREQUEST)) as exc_info:
            client.parts.update(
                number=part_number,
                new_number=long_number
            )
        
        if auth_type == "user":
            error_message = str(exc_info.value).lower()
            assert "60" in error_message or "length" in error_message or "long" in error_message
    
    def test_update_part_name_too_long(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part with name > 255 chars."""
        
        # Create a part
        part_number = f"PART-{timestamp}"
        part = client.parts.create(number=part_number)
        assert_create_part_success(part)
        
        # Try to update with long name (> 255 chars)
        long_name = "Y" * 256
        from tofupilot.v2.errors import ErrorBADREQUEST
        
        # Both user and station should fail with long name
        with pytest.raises((APIError, ErrorBADREQUEST)) as exc_info:
            client.parts.update(
                number=part_number,
                name=long_name
            )
        
        if auth_type == "user":
            error_message = str(exc_info.value).lower()
            assert "255" in error_message or "length" in error_message or "long" in error_message
    
    def test_update_no_fields_provided(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part without providing any fields to update."""
        
        # Create a part
        part_number = f"PART-{timestamp}"
        part = client.parts.create(number=part_number)
        assert_create_part_success(part)
        
        # Try to update without any fields
        from tofupilot.v2.errors import ErrorBADREQUEST
        
        # Both user and station should fail without fields
        with pytest.raises((APIError, ErrorBADREQUEST)) as exc_info:
            client.parts.update(number=part_number)
        
        if auth_type == "user":
            error_message = str(exc_info.value).lower()
            assert "at least one" in error_message or "required" in error_message or "missing" in error_message
    
    def test_update_case_insensitive_conflict(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that part number uniqueness is case-insensitive on update."""
        
        # Create two parts
        part1_number = f"part-lower-{timestamp}"
        part1 = client.parts.create(number=part1_number)
        assert_create_part_success(part1)
        
        part2_number = f"PART-UPPER-{timestamp}"
        part2 = client.parts.create(number=part2_number)
        assert_create_part_success(part2)
        
        # Try to update part2 to have uppercase version of part1's number
        # This should fail due to case-insensitive conflict
        new_number = f"PART-LOWER-{timestamp}"  # Uppercase version of existing part1
        
        if auth_type == "station":
            # Station has limited access - update may succeed but not change anything
            with assert_station_access_limited("update part number with case insensitive conflict"):
                result = client.parts.update(
                    number=part2_number,
                    new_number=new_number
                )
                # Verify the number didn't change (silent failure)
                assert result.number != new_number, "Station should not be able to update part number"
                assert result.number == f"PART-UPPER-{timestamp}", "Part number should remain unchanged"
        else:
            # User should get CONFLICT error due to case-insensitive matching
            with pytest.raises(ErrorCONFLICT) as exc_info:
                client.parts.update(
                    number=part2_number,
                    new_number=new_number
                )
            
            # Verify error message mentions the conflict
            error_message = str(exc_info.value).lower()
            assert "already exists" in error_message or "conflict" in error_message
    
    def test_update_to_same_number(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part to its current number (should succeed)."""
        part_number = f"PART-SAME-{timestamp}"
        
        # Create a part
        part = client.parts.create(
            number=part_number,
            name="Original Name"
        )
        assert_create_part_success(part)
        
        # Update with same number but different name
        if auth_type == "station":
            # Station has limited access - update may succeed but not change anything
            with assert_station_access_limited("update part with same number"):
                result = client.parts.update(
                    number=part_number,
                    new_number=part_number,  # Same number
                    name="Updated Name"
                )
                # Verify the name didn't change (silent failure)
                assert result.number == part_number  # Number stays the same
                assert result.name == "Original Name", "Station should not be able to update part name"
        else:
            result = client.parts.update(
                number=part_number,
                new_number=part_number,  # Same number
                name="Updated Name"
            )
            
            # Should succeed
            assert result.number == part_number
            assert result.name == "Updated Name"