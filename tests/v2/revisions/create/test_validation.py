"""Test revision creation validation rules."""

import pytest
from datetime import datetime, timezone
import uuid
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError, ErrorCONFLICT, ErrorNOTFOUND
from ..utils import assert_create_revision_success
from ...parts.utils import assert_create_part_success


class TestCreateRevisionValidation:
    """Test revision creation validation scenarios."""
    
    @pytest.fixture
    def test_part(self, client: TofuPilot, auth_type: str, timestamp: str) -> tuple[str, str]:
        """Create a test part for revision validation tests."""
            
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-VAL-{timestamp}-{unique_id}"
        
        result = client.parts.create(
            number=part_number,
            name=f"Validation Test Part {unique_id}"
        )
        assert_create_part_success(result)
        return result.id, part_number
    
    def test_empty_revision_number_fails(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test that creating a revision with empty number fails."""
            
        _, part_number = test_part
        with pytest.raises(APIError) as exc_info:
            client.parts.revisions.create(part_number=part_number, number="")
        
        # Verify the error is about validation
        error_message = str(exc_info.value).lower()
        assert "validation" in error_message or "invalid" in error_message or "empty" in error_message
    
    def test_revision_number_too_long_fails(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test that creating a revision with number > 60 chars fails."""
            
        _, part_number = test_part
        # Create a 61-character revision number
        long_revision_number = "R" * 61
        
        with pytest.raises(APIError) as exc_info:
            client.parts.revisions.create(part_number=part_number, number=long_revision_number)
        
        # Verify the error is about length
        error_message = str(exc_info.value).lower()
        assert "60" in error_message or "length" in error_message or "long" in error_message
    
    def test_invalid_part_number_fails(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test that creating a revision with invalid part_number fails."""
            
        revision_number = f"REV-FAIL-{timestamp}"
        fake_part_id = "00000000-0000-0000-0000-000000000000"
        
        with pytest.raises(ErrorNOTFOUND) as exc_info:
            client.parts.revisions.create(part_number=fake_part_id, number=revision_number)
        
        # Verify the error is about part not found
        error_message = str(exc_info.value).lower()
        assert "not found" in error_message or "part" in error_message
    
    def test_malformed_uuid_part_number_fails(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test that creating a revision with non-existent part fails."""
            
        revision_number = f"REV-NONEXISTENT-{timestamp}"
        
        with pytest.raises(ErrorNOTFOUND) as exc_info:
            client.parts.revisions.create(part_number="NONEXISTENT-PART-12345", number=revision_number)
        
        # Verify the error is about part not found
        error_message = str(exc_info.value).lower()
        assert "not found" in error_message
    
    def test_duplicate_revision_number_same_part_fails(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str, timestamp: str) -> None:
        """Test that creating duplicate revision numbers for the same part fails."""
            
        _, part_number = test_part
        # Create unique revision number
        revision_number = f"REV-DUP-{timestamp}"
        
        # Create first revision
        result1 = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        assert_create_revision_success(result1)
        
        # Try to create second revision with same number for same part - should fail
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.parts.revisions.create(
                part_number=part_number,
                number=revision_number
            )
        
        # Verify the error is about duplicate/conflict
        error_message = str(exc_info.value).lower()
        assert "already exists" in error_message or "conflict" in error_message or "duplicate" in error_message
    
    def test_same_revision_number_different_parts_succeeds(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test that same revision number for different parts succeeds."""
            
        revision_number = f"REV-SAME-{timestamp}"
        
        # Create two different parts
        part1_result = client.parts.create(
            number=f"PART-1-{timestamp}",
            name="Part 1 for Same Revision Test"
        )
        assert_create_part_success(part1_result)
        
        part2_result = client.parts.create(
            number=f"PART-2-{timestamp}",
            name="Part 2 for Same Revision Test"
        )
        assert_create_part_success(part2_result)
        
        # Create revision with same number for first part
        rev1_result = client.parts.revisions.create(
            part_number=f"PART-1-{timestamp}",
            number=revision_number
        )
        assert_create_revision_success(rev1_result)
        
        # Create revision with same number for second part - should succeed
        rev2_result = client.parts.revisions.create(
            part_number=f"PART-2-{timestamp}",
            number=revision_number
        )
        assert_create_revision_success(rev2_result)
        
        # Verify they are different revisions
        assert rev1_result.id != rev2_result.id
    
    def test_revision_number_case_insensitive(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str, timestamp: str) -> None:
        """Test that revision numbers are case-insensitive for uniqueness."""
        from tofupilot.v2.errors import ErrorCONFLICT
            
        _, part_number = test_part
        
        # Create revision with lowercase
        lower_result = client.parts.revisions.create(
            part_number=part_number,
            number=f"rev-case-{timestamp}"
        )
        assert_create_revision_success(lower_result)
        
        # Try to create revision with uppercase - should fail due to case-insensitive matching
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.parts.revisions.create(
                part_number=part_number,
                number=f"REV-CASE-{timestamp}"
            )
        
        # Verify error message mentions the conflict
        error_message = str(exc_info.value).lower()
        assert "already exists" in error_message or "conflict" in error_message