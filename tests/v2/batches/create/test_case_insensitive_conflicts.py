"""Test case-insensitive conflict detection for batch creation."""
import pytest
import uuid
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorCONFLICT


@pytest.mark.parametrize("client", ["user"], indirect=True)
class TestBatchCaseInsensitiveConflicts:
    """Test that batch creation detects case-insensitive conflicts."""

    def test_batch_create_case_insensitive_conflict(self, client: TofuPilot):
        """Test that creating batches with same number but different case throws conflict error."""
        batch_number = f"BATCH-{uuid.uuid4()}"
        
        # Create first batch with uppercase
        batch1 = client.batches.create(number=batch_number.upper())
        assert batch1.id
        
        # Try to create with lowercase - should fail with 409 conflict
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.batches.create(number=batch_number.lower())
        
        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value).lower()
        
        # Also test with mixed case and whitespace
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.batches.create(number=f"  {batch_number.title()}  ")
        
        assert exc_info.value.status_code == 409

    def test_batch_create_no_conflict_different_numbers(self, client: TofuPilot):
        """Test that creating batches with different numbers works."""
        batch1_number = f"BATCH-{uuid.uuid4()}"
        batch2_number = f"BATCH-{uuid.uuid4()}"
        
        # Create both batches successfully
        batch1 = client.batches.create(number=batch1_number)
        batch2 = client.batches.create(number=batch2_number)
        
        assert batch1.id != batch2.id

    def test_batch_create_whitespace_normalization_conflict(self, client: TofuPilot):
        """Test that whitespace is normalized in conflict detection."""
        batch_number = f"BATCH-{uuid.uuid4()}"
        
        # Create with spaces
        batch1 = client.batches.create(number=f"  {batch_number}  ")
        assert batch1.id
        
        # Try to create without spaces - should fail with proper 409 conflict
        with pytest.raises(ErrorCONFLICT) as exc_info:
            client.batches.create(number=batch_number)
        
        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value).lower()