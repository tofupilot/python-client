"""Test complete batch lifecycle including creation, usage, and deletion."""

from datetime import datetime, timezone
from typing import List
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_batch_success, assert_delete_batch_success, assert_get_batches_success
from ...utils import assert_station_access_forbidden, assert_station_access_limited


class TestBatchDeleteLifecycle:
    
    def test_complete_batch_lifecycle(self, client: TofuPilot, auth_type: str) -> None:
        """Test complete lifecycle: create batch, use it, then delete it."""
        # Create batch
        BATCH_NUMBER = f"AutomatedTest-V2-Lifecycle-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        batch_result = client.batches.create(number=BATCH_NUMBER)
        assert_create_batch_success(batch_result)
        batch_id = batch_result.id
        
        # Verify batch exists
        list_result = client.batches.list(ids=[batch_id])
        assert_get_batches_success(list_result)
        assert len(list_result.data) == 1
        assert list_result.data[0].number == BATCH_NUMBER
        
        if auth_type == "user":
            # Users can delete batches
            delete_result = client.batches.delete(number=BATCH_NUMBER)
            assert_delete_batch_success(delete_result)
            
            # Verify batch is gone
            list_result = client.batches.list(ids=[batch_id])
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 0
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete batch"):
                client.batches.delete(number=BATCH_NUMBER)
    
    def test_multiple_batch_operations(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating and deleting multiple batches."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        batch_ids: List[str] = []
        batch_numbers: List[str] = []
        
        # Create multiple batches
        for i in range(3):
            batch_number = f"AutomatedTest-V2-Multi-{i}-{timestamp}"
            batch = client.batches.create(number=batch_number)
            assert_create_batch_success(batch)
            batch_ids.append(batch.id)
            batch_numbers.append(batch_number)
        
        # Verify all exist
        list_result = client.batches.list(ids=batch_ids)
        assert_get_batches_success(list_result)
        assert len(list_result.data) == 3
        
        if auth_type == "user":
            # Users can delete batches
            for batch_number in batch_numbers:
                delete_result = client.batches.delete(number=batch_number)
                assert_delete_batch_success(delete_result)
            
            # Verify all are gone
            list_result = client.batches.list(ids=batch_ids)
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 0
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            for batch_number in batch_numbers:
                with assert_station_access_forbidden(f"delete batch {batch_number}"):
                    client.batches.delete(number=batch_number)
    
    def test_batch_deletion_does_not_affect_others(self, client: TofuPilot, auth_type: str) -> None:
        """Test that deleting one batch doesn't affect others."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        # Create two batches
        batch1_number = f"KEEP-BATCH-{timestamp}"
        batch2_number = f"DELETE-BATCH-{timestamp}"
        batch1 = client.batches.create(number=batch1_number)
        batch2 = client.batches.create(number=batch2_number)
        assert_create_batch_success(batch1)
        assert_create_batch_success(batch2)
        
        if auth_type == "user":
            # Users can delete batches
            delete_result = client.batches.delete(number=batch2_number)
            assert_delete_batch_success(delete_result)
            
            # Verify first batch still exists
            list_result = client.batches.list(ids=[batch1.id])
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 1
            assert list_result.data[0].id == batch1.id
            
            # Verify second batch is gone
            list_result = client.batches.list(ids=[batch2.id])
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 0
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete batch"):
                client.batches.delete(number=batch2_number)
    
    def test_batch_with_special_characters_deletion(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting batches with special characters in their numbers."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        # Create batch with special characters (URL-safe but non-alphanumeric)
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        special_batch_number = f"SPECIAL-123_TEST-{timestamp}-{unique_id}"
        special_batch = client.batches.create(number=special_batch_number)
        assert_create_batch_success(special_batch)
        
        if auth_type == "user":
            # Users can delete batches
            delete_result = client.batches.delete(number=special_batch_number)
            assert_delete_batch_success(delete_result)
            
            # Verify it's gone
            list_result = client.batches.list(ids=[special_batch.id])
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 0
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete batch with special characters"):
                client.batches.delete(number=special_batch_number)