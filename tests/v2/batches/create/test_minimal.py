"""Test minimal batch creation with just required parameters."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_batch_success, assert_get_batches_success


class TestCreateBatchMinimal:

    def test_minimal_batch_creation(self, client: TofuPilot) -> None:
        """Test minimal batch creation with all required parameters."""
        # Test constants
        BATCH_NUMBER = f"AutomatedTest-V2-Minimal-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        # Create batch using SDK
        result = client.batches.create(
            number=BATCH_NUMBER,
        )
        
        # Verify successful response
        assert_create_batch_success(result)
        
        # Test batches.list to verify it's in the list
        list_result = client.batches.list(ids=[result.id])
        assert_get_batches_success(list_result)
        assert len(list_result.data) == 1
        listed_batch = list_result.data[0]
        assert listed_batch.id == result.id
        assert listed_batch.number == BATCH_NUMBER
        
    def test_batch_creation_with_max_length_number(self, client: TofuPilot) -> None:
        """Test batch creation with maximum allowed length for number (60 chars)."""
        # Create a 60-character batch number with microseconds and UUID for uniqueness
        import uuid
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        unique_id = str(uuid.uuid4())[:8]
        prefix = f"MAX-LEN-{timestamp}-{unique_id}-"
        padding_length = 60 - len(prefix)
        BATCH_NUMBER = prefix + "X" * padding_length
        
        assert len(BATCH_NUMBER) == 60, f"Expected 60 chars, got {len(BATCH_NUMBER)}"
        
        # Create batch
        result = client.batches.create(
            number=BATCH_NUMBER,
        )
        
        # Verify successful response
        assert_create_batch_success(result)
        
        # Verify by listing the batch
        list_result = client.batches.list(ids=[result.id])
        assert_get_batches_success(list_result)
        assert len(list_result.data) == 1
        assert list_result.data[0].number == BATCH_NUMBER
        assert len(list_result.data[0].number) == 60