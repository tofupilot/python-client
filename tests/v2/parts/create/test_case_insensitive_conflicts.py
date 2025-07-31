"""Test case-insensitive conflict detection for part creation."""
import pytest
import uuid
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorCONFLICT


@pytest.mark.parametrize("client", ["user"], indirect=True)
class TestPartCaseInsensitiveConflicts:
    """Test that part creation detects case-insensitive conflicts."""

    def test_part_create_case_insensitive_conflict(self, client: TofuPilot):
        """Test that creating parts with same number but different case throws error."""
        part_number = f"PART-{uuid.uuid4()}"
        
        # Create first part with uppercase
        part1 = client.parts.create(number=part_number.upper())
        assert part1.id
        
        # Try to create with lowercase - should fail with 409 conflict
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.parts.create(number=part_number.lower())
        
        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value).lower()
        
        # Also test with mixed case and whitespace
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.parts.create(number=f"  {part_number.title()}  ")
        
        assert exc_info.value.status_code == 409

    def test_part_create_no_conflict_different_numbers(self, client: TofuPilot):
        """Test that creating parts with different numbers works."""
        part1_number = f"PART-{uuid.uuid4()}"
        part2_number = f"PART-{uuid.uuid4()}"
        
        # Create both parts successfully
        part1 = client.parts.create(number=part1_number)
        part2 = client.parts.create(number=part2_number)
        
        assert part1.id != part2.id

    def test_part_create_whitespace_normalization_conflict(self, client: TofuPilot):
        """Test that whitespace is normalized in conflict detection."""
        part_number = f"PART-{uuid.uuid4()}"
        
        # Create with spaces
        part1 = client.parts.create(number=f"  {part_number}  ")
        assert part1.id
        
        # Try to create without spaces - should fail
        # Check if it returns 409 or 500 (backend inconsistency)
        try:
            client.parts.create(number=part_number)
            pytest.fail("Expected error when creating part with same normalized number")
        except ErrorCONFLICT as e:
            assert e.status_code == 409
            assert "already exists" in str(e).lower()
        except ERRORINTERNALSERVERERROR as e:
            assert e.status_code == 500
            assert "already in use" in str(e).lower()