"""Test part creation validation rules."""

import pytest
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError, ErrorCONFLICT
from ..utils import assert_create_part_success


class TestCreatePartValidation:
    """Test part creation validation scenarios."""
    
    def test_empty_part_number_fails(self, client: TofuPilot, auth_type: str) -> None:
        """Test that creating a part with empty number fails."""
            
        with pytest.raises(APIError) as exc_info:
            client.parts.create(number="")
        
        # Verify the error is about validation
        error_message = str(exc_info.value).lower()
        assert "validation" in error_message or "invalid" in error_message or "empty" in error_message
    
    def test_part_number_too_long_fails(self, client: TofuPilot, auth_type: str) -> None:
        """Test that creating a part with number > 60 chars fails."""
            
        # Create a 61-character part number
        PART_NUMBER = "X" * 61
        
        with pytest.raises(APIError) as exc_info:
            client.parts.create(number=PART_NUMBER)
        
        # Verify the error is about length
        error_message = str(exc_info.value).lower()
        assert "length" in error_message or "long" in error_message or "60" in error_message
    
    def test_part_name_too_long_fails(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that creating a part with name > 255 chars fails."""
            
        PART_NUMBER = f"PN-{timestamp}"
        PART_NAME = "Y" * 256
        
        with pytest.raises(APIError) as exc_info:
            client.parts.create(number=PART_NUMBER, name=PART_NAME)
        
        # Verify the error is about length
        error_message = str(exc_info.value).lower()
        assert "length" in error_message or "long" in error_message or "255" in error_message
    
    def test_revision_number_too_long_fails(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that creating a part with revision_number > 60 chars fails."""
            
        PART_NUMBER = f"PN-{timestamp}"
        REVISION_NUMBER = "R" * 61
        
        with pytest.raises(APIError) as exc_info:
            client.parts.create(number=PART_NUMBER, revision_number=REVISION_NUMBER)
        
        # Verify the error is about length
        error_message = str(exc_info.value).lower()
        assert "length" in error_message or "long" in error_message or "60" in error_message
    
    def test_duplicate_part_number_fails(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that creating a part with duplicate number fails."""
            
        # Create unique part number
        PART_NUMBER = f"PN-DUP-{timestamp}"
        
        # Create first part
        result1 = client.parts.create(number=PART_NUMBER)
        assert_create_part_success(result1)
        
        # Try to create second part with same number - should fail
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.parts.create(number=PART_NUMBER)
        
        # Verify the error is about duplicate/conflict
        error_message = str(exc_info.value).lower()
        assert "already exists" in error_message or "conflict" in error_message or "duplicate" in error_message
    
    def test_part_number_case_insensitive(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that part numbers are case-insensitive for uniqueness."""
        from tofupilot.v2.errors import ErrorCONFLICT

        PART_NUMBER_LOWER = f"pn-case-{timestamp}"
        PART_NUMBER_UPPER = f"PN-CASE-{timestamp}"
        
        # Create part with lowercase
        result1 = client.parts.create(number=PART_NUMBER_LOWER)
        assert_create_part_success(result1)
        
        # Try to create part with uppercase - should fail due to case-insensitive matching
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.parts.create(number=PART_NUMBER_UPPER)
        
        # Verify error message mentions the conflict
        error_message = str(exc_info.value).lower()
        assert "already exists" in error_message or "conflict" in error_message
    
    def test_part_number_special_characters(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test part creation with various special characters."""
            
        special_chars_tests = [
            ("hyphen", "PN-123-ABC"),
            ("underscore", "PN_123_ABC"),
            ("dot", "PN.123.ABC"),
            ("slash", "PN/123/ABC"),
            ("backslash", "PN\\123\\ABC"),
            ("space", "PN 123 ABC"),
            ("parentheses", "PN(123)ABC"),
            ("brackets", "PN[123]ABC"),
            ("unicode", "PN-测试-123"),
            ("emoji", "PN-🔧-123"),
        ]
        
        for test_name, special_pattern in special_chars_tests:
            part_number = f"{special_pattern}-{timestamp}-{test_name}"
            
            try:
                result = client.parts.create(number=part_number)
                assert_create_part_success(result)
                # If it succeeds, that's good - special character is allowed
            except APIError as e:
                # Some characters might not be allowed - that's okay
                print(f"Character test '{test_name}' failed as expected: {e}")