"""Test batch creation validation rules."""

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError, ErrorBADREQUEST


class TestCreateBatchValidation:

    def test_empty_batch_number_fails(self, client: TofuPilot, auth_type: str) -> None:
        """Test that creating a batch with empty number fails."""
        with pytest.raises((APIError, ErrorBADREQUEST)) as exc_info:
            client.batches.create(number="")
        
        # Verify the error is about validation
        error_message = str(exc_info.value).lower()
        assert "validation" in error_message or "invalid" in error_message or "empty" in error_message
    
    def test_batch_number_too_long_fails(self, client: TofuPilot, auth_type: str) -> None:
        """Test that creating a batch with number > 100 chars fails."""
        # Create a 101-character batch number
        BATCH_NUMBER = "X" * 101
        
        with pytest.raises((APIError, ErrorBADREQUEST)) as exc_info:
            client.batches.create(number=BATCH_NUMBER)
        
        # Verify the error is about validation (backend returns generic validation message)
        error_message = str(exc_info.value).lower()
        assert "validation" in error_message or "invalid" in error_message or "failed" in error_message
    
    def test_batch_number_with_special_characters(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test batch creation with various special characters."""
        from datetime import datetime, timezone
        from ..utils import assert_create_batch_success
        
        # Test various special characters - only alphanumeric, dash, and underscore are allowed
        # Based on testing, the regex appears to be: ^[a-zA-Z0-9_-]+$
        special_chars_tests = [
            ("dash", "BATCH-123-TEST"),
            ("underscore", "BATCH_123_TEST"),
            ("alphanumeric", "BATCH123TEST"),
            ("mixed", "BATCH-123_TEST"),
        ]
        
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        for test_name, special_pattern in special_chars_tests:
            batch_number = f"{special_pattern}-{timestamp}-{unique_id}-{test_name}"
            
            print(f"Testing batch number: {batch_number}")
            result = client.batches.create(number=batch_number)
            assert_create_batch_success(result)

    invalid_chars = [
            ("slash", "BATCH/123"),
            ("backslash", "BATCH\\123"),
            ("space", "BATCH 123"),
            ("parentheses", "BATCH(123)"),
            ("brackets", "BATCH[123]"),
            ("hash", "BATCH#123"),
            ("at", "BATCH@123"),
            ("ampersand", "BATCH&123"),
            ("equals", "BATCH=123"),
            ("comma", "BATCH,123"),
            ("semicolon", "BATCH;123"),
            ("quotes", 'BATCH"123"'),
            ("apostrophe", "BATCH'123'"),
        ]
    
    @pytest.mark.parametrize("test_name, special_pattern", invalid_chars, ids=[name for (name, _) in invalid_chars])
    def test_batch_number_with_invalid_characters_fails(self, client: TofuPilot, auth_type: str, test_name, special_pattern, timestamp) -> None:
        """Test that batch creation fails with invalid special characters."""
        import uuid
        from datetime import datetime, timezone
        
        # Test various special characters that should NOT be allowed
        
        unique_id = str(uuid.uuid4())[:8]
        
        batch_number = f"{special_pattern}-{timestamp}-{unique_id}-{test_name}"
        
        with pytest.raises(ErrorBADREQUEST) as exc_info:
            print(f"Testing invalid batch number: {batch_number}")
            client.batches.create(number=batch_number)
        
        error_message = str(exc_info.value).lower()
        # Backend returns generic validation message for invalid characters
        assert any(msg in error_message for msg in [
            "validation",
            "invalid",
            "failed"
        ]), f"Expected validation error message for {test_name}, got: {error}"