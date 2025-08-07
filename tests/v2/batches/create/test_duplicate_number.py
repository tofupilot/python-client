"""Test batch creation with duplicate numbers."""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorCONFLICT
from ..utils import assert_create_batch_success

class TestCreateBatchDuplicateNumber:

    def test_duplicate_batch_number_fails(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that creating a batch with duplicate number fails within same organization."""
        # Test constants
        BATCH_NUMBER = f"AutomatedTest-V2-Duplicate-{timestamp}"
        
        # Create first batch
        result1 = client.batches.create(number=BATCH_NUMBER)
        assert_create_batch_success(result1)
        
        # Try to create second batch with same number - should fail
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.batches.create(number=BATCH_NUMBER)
        
        # Verify the error is about duplicate/conflict
        error_message = str(exc_info.value).lower()
        assert "already exists" in error_message or "conflict" in error_message or "duplicate" in error_message
    
    def test_batch_number_uniqueness_case_insensitive(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that batch numbers are case-insensitive for uniqueness."""
        # Test constants
        BATCH_NUMBER_LOWER = f"automatedtest-v2-case-{timestamp}"
        BATCH_NUMBER_UPPER = f"AUTOMATEDTEST-V2-CASE-{timestamp}"
        
        # Create batch with lowercase
        result1 = client.batches.create(number=BATCH_NUMBER_LOWER)
        assert_create_batch_success(result1)
        
        # Try to create batch with uppercase - should fail due to case-insensitive matching
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.batches.create(number=BATCH_NUMBER_UPPER)
        
        # Verify the error is about duplicate
        error_message = str(exc_info.value).lower()
        assert "already in use" in error_message or "duplicate" in error_message or "conflict" in error_message or "already exists" in error_message