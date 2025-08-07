"""Test deleting empty batches."""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_batch_success, assert_delete_batch_success, assert_get_batches_success
from ...utils import assert_station_access_forbidden


class TestDeleteEmptyBatch:
    
    def test_delete_empty_batch_success(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test deleting an empty batch - behavior differs by auth type.
        
        Users: Can successfully delete batches they have access to.
        Stations: Cannot delete batches (access policy only allows select/insert).
        """
        # Create a batch
        BATCH_NUMBER = f"AutomatedTest-V2-Delete-Empty-{timestamp}"
        
        create_result = client.batches.create(number=BATCH_NUMBER)
        assert_create_batch_success(create_result)
        batch_id = create_result.id
        
        if auth_type == "user":
            # Users have full access to manage batches in their organization
            delete_result = client.batches.delete(number=BATCH_NUMBER)
            assert_delete_batch_success(delete_result)
            assert delete_result.id == batch_id
            
            # Verify batch no longer exists
            list_result = client.batches.list(ids=[batch_id])
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 0
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete empty batch"):
                client.batches.delete(number=BATCH_NUMBER)
    
    def test_delete_non_existent_batch(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting a non-existent batch returns 404 for users, 403 for stations."""
        fake_number = "NON-EXISTENT-BATCH-123456789"
        
        if auth_type == "user":
            with pytest.raises(ErrorNOTFOUND) as exc_info:
                client.batches.delete(number=fake_number)
            
            # Should be 404 not found
            error_message = str(exc_info.value).lower()
            assert "not found" in error_message or "404" in error_message
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete non-existent batch"):
                client.batches.delete(number=fake_number)
    
    def test_delete_already_deleted_batch(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test deleting an already deleted batch fails.
        
        Users: Can delete once, then subsequent deletes fail with NOT_FOUND.
        Stations: Cannot delete batches at all due to access restrictions.
        """
        # Create and delete a batch
        BATCH_NUMBER = f"AutomatedTest-V2-Delete-Twice-{timestamp}"
        
        create_result = client.batches.create(number=BATCH_NUMBER)
        assert_create_batch_success(create_result)
        
        if auth_type == "user":
            # First deletion should succeed for users with manage access
            delete_result = client.batches.delete(number=BATCH_NUMBER)
            assert_delete_batch_success(delete_result)
            
            # Second deletion should fail - batch no longer exists
            with pytest.raises(ErrorNOTFOUND) as exc_info:
                client.batches.delete(number=BATCH_NUMBER)
            
            error_message = str(exc_info.value).lower()
            assert "not found" in error_message or "404" in error_message
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete already deleted batch"):
                client.batches.delete(number=BATCH_NUMBER)
    
    def test_create_delete_recreate_same_number(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test that after deleting a batch, the same number can be reused.
        
        Users: Can delete and recreate batches with the same number.
        Stations: Cannot delete batches, so recreation test is not applicable.
        """
        BATCH_NUMBER = f"AutomatedTest-V2-Recreate-{timestamp}"
        
        # Create first batch
        result1 = client.batches.create(number=BATCH_NUMBER)
        assert_create_batch_success(result1)
        
        if auth_type == "user":
            # Users can delete batches and reuse the number
            delete_result = client.batches.delete(number=BATCH_NUMBER)
            assert_delete_batch_success(delete_result)
            
            # Create new batch with same number - should succeed
            result2 = client.batches.create(number=BATCH_NUMBER)
            assert_create_batch_success(result2)
            assert result2.id != result1.id  # Should be different batch
            
            # Verify via list that the batch has the correct number
            list_result = client.batches.list(ids=[result2.id])
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 1
            assert list_result.data[0].number == BATCH_NUMBER
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete batch for recreation test"):
                client.batches.delete(number=BATCH_NUMBER)