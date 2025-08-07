"""Test revision update field modifications."""

from datetime import datetime, timezone
from typing import List
import pytest
import uuid
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND, ErrorCONFLICT
from ..utils import assert_create_revision_success, assert_update_revision_success
from ...parts.utils import assert_create_part_success


class TestUpdateRevisionFields:
    """Test updating revision fields."""
    
    @pytest.fixture
    def test_part(self, client: TofuPilot, auth_type: str, timestamp: str) -> tuple[str, str]:
        """Create a test part for revision update tests."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-UPD-{timestamp}-{unique_id}"
        
        result = client.parts.create(
            number=part_number,
            name=f"Update Test Part {unique_id}"
        )
        assert_create_part_success(result)
        return result.id, part_number
    
    @pytest.fixture
    def test_revision(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str, timestamp: str) -> tuple[str, str, str]:
        """Create a test revision for update tests. Returns (part_id, part_number, revision_number)."""
            
        part_id, part_number = test_part
        revision_number = f"REV-ORIGINAL-{timestamp}"
        
        result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        assert_create_revision_success(result)
        return part_id, part_number, revision_number
    
    def test_update_revision_number(self, client: TofuPilot, test_revision: tuple[str, str, str], auth_type: str, timestamp: str) -> None:
        """Test updating revision number."""
            
        part_id, part_number, old_revision_number = test_revision
        new_number = f"REV-UPDATED-{timestamp}"
        
        # Both users and stations can update revision numbers
        
        # Update the revision number
        result = client.parts.revisions.update(
            part_number=part_number,
            revision_number=old_revision_number,
            number=new_number
        )
        
        assert_update_revision_success(result)
        
        # Verify by getting the specific revision
        get_result = client.parts.revisions.get(
            part_number=part_number,
            revision_number=new_number
        )
        assert get_result.id == result.id
        assert get_result.number == new_number
    
    def test_update_revision_number_to_edge_lengths(self, client: TofuPilot, test_revision: tuple[str, str, str], auth_type: str, timestamp: str) -> None:
        """Test updating revision number to edge case lengths."""
            
        part_id, part_number, old_revision_number = test_revision
        
        # Both users and stations can update revision numbers
        
        # Test minimum length (1 character) - make it unique
        short_number = f"A{timestamp[-6:]}"  # Use last 6 digits to make unique
        result = client.parts.revisions.update(
            part_number=part_number,
            revision_number=old_revision_number,
            number=short_number
        )
        assert_update_revision_success(result)
        
        # Test near maximum length (60 characters)
        long_number = f"REV-{timestamp}-" + "X" * (60 - len(f"REV-{timestamp}-"))
        result = client.parts.revisions.update(
            part_number=part_number,
            revision_number=short_number,  # Current revision number after previous update
            number=long_number
        )
        assert_update_revision_success(result)
        assert len(long_number) == 60
    
    def test_update_nonexistent_revision_fails(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test updating non-existent revision fails."""
            
        _, part_number = test_part
        fake_revision_number = "NONEXISTENT-REV"
        
        with pytest.raises(ErrorNOTFOUND) as exc_info:
            client.parts.revisions.update(
                part_number=part_number,
                revision_number=fake_revision_number,
                number="SHOULD-FAIL"
            )
        
        # Verify the error is about revision not found
        error_message = str(exc_info.value).lower()
        assert "not found" in error_message
    
    def test_update_to_duplicate_number_same_part_fails(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str, timestamp: str) -> None:
        """Test updating to duplicate revision number for same part fails."""
            
        _, part_number = test_part
        
        # Both users and stations can update revisions
        
        # Create two revisions for the same part
        rev1_number = f"REV-FIRST-{timestamp}"
        rev1_result = client.parts.revisions.create(
            part_number=part_number,
            number=rev1_number
        )
        assert_create_revision_success(rev1_result)
        
        rev2_number = f"REV-SECOND-{timestamp}"
        rev2_result = client.parts.revisions.create(
            part_number=part_number,
            number=rev2_number
        )
        assert_create_revision_success(rev2_result)
        
        # Try to update rev2 to have the same number as rev1 - should fail
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.parts.revisions.update(
                part_number=part_number,
                revision_number=rev2_number,
                number=rev1_number
            )
        
        # Verify the error is about conflict/duplicate
        error_message = str(exc_info.value).lower()
        assert "already exists" in error_message or "conflict" in error_message
    
    def test_update_to_same_number_different_parts_succeeds(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating to same revision number for different parts succeeds."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Both users and stations can update revisions across different parts
        
        # Create two different parts
        part1_number = f"PART-1-UPD-{timestamp}-{unique_id}"
        part1_result = client.parts.create(
            number=part1_number,
            name="Update Test Part 1"
        )
        assert_create_part_success(part1_result)
        
        part2_number = f"PART-2-UPD-{timestamp}-{unique_id}"
        part2_result = client.parts.create(
            number=part2_number,
            name="Update Test Part 2"
        )
        assert_create_part_success(part2_result)
        
        # Create revisions for both parts
        rev1_number = f"REV-DIFF-1-{timestamp}"
        rev1_result = client.parts.revisions.create(
            part_number=part1_number,
            number=rev1_number
        )
        assert_create_revision_success(rev1_result)
        
        rev2_number = f"REV-DIFF-2-{timestamp}"
        rev2_result = client.parts.revisions.create(
            part_number=part2_number,
            number=rev2_number
        )
        assert_create_revision_success(rev2_result)
        
        # Update both to have the same number - should succeed since different parts
        same_number = f"REV-SAME-ACROSS-PARTS-{timestamp}"
        
        # Update rev1 first
        result1 = client.parts.revisions.update(
            part_number=part1_number,
            revision_number=rev1_number,
            number=same_number
        )
        assert_update_revision_success(result1)
        
        # Update rev2 to same number - should succeed since different parts
        result2 = client.parts.revisions.update(
            part_number=part2_number,
            revision_number=rev2_number,
            number=same_number
        )
        assert_update_revision_success(result2)
    
    def test_update_no_fields_provided_fails(self, client: TofuPilot, test_revision: tuple[str, str, str], auth_type: str) -> None:
        """Test update with no fields provided fails."""
            
        part_id, part_number, revision_number = test_revision
        
        # Try to update without providing any fields
        with pytest.raises(Exception) as exc_info:
            # This should fail because no fields are provided to update
            client.parts.revisions.update(
                part_number=part_number,
                revision_number=revision_number
                # No fields provided - should fail
            )
        
        # Should get some kind of validation error
        error_message = str(exc_info.value).lower()
        # The specific error message may vary based on implementation
        assert len(error_message) > 0  # Some error should be present
    
    def test_update_preserves_part_relationship(self, client: TofuPilot, test_revision: tuple[str, str, str], auth_type: str, timestamp: str) -> None:
        """Test that updating revision preserves part relationship."""
            
        part_id, part_number, old_revision_number = test_revision
        new_number = f"REV-PRESERVE-{timestamp}"
        
        # Both users and stations can update revisions
        
        # Update revision number
        result = client.parts.revisions.update(
            part_number=part_number,
            revision_number=old_revision_number,
            number=new_number
        )
        assert_update_revision_success(result)
        
        # Verify part relationship is preserved
        get_result = client.parts.revisions.get(
            part_number=part_number,
            revision_number=new_number
        )
        assert get_result.part.id == part_id
        assert get_result.number == new_number