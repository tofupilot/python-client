"""Test ID-based filtering in batches.list()."""

import pytest
from typing import List
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_batch_success, assert_get_batches_success


class TestBatchesIdsFiltering:
    """Test filtering batches by IDs."""
    
    @pytest.fixture
    def test_batches_for_ids(self, client: TofuPilot) -> List[models.BatchCreateResponse]:
        """Create test batches for ID filtering tests."""
        import uuid
        test_batches: List[models.BatchCreateResponse] = []
        for i in range(5):
            batch = client.batches.create(
                number=f"ID-FILTER-TEST-{uuid.uuid4()}"
            )
            assert_create_batch_success(batch)
            test_batches.append(batch)
            
        return test_batches

    def test_filter_by_single_id(self, client: TofuPilot, test_batches_for_ids: List[models.BatchCreateResponse]):
        """Test filtering by a single batch ID."""
        target_batch = test_batches_for_ids[0]
        
        result = client.batches.list(ids=[target_batch.id])
        assert_get_batches_success(result)
        
        assert len(result.data) == 1
        assert result.data[0].id == target_batch.id
        # Verify the batch exists

    def test_filter_by_multiple_ids(self, client: TofuPilot, test_batches_for_ids: List[models.BatchCreateResponse]):
        """Test filtering by multiple batch IDs."""
        target_ids = [test_batches_for_ids[0].id, test_batches_for_ids[2].id, test_batches_for_ids[4].id]
        
        result = client.batches.list(ids=target_ids)
        assert_get_batches_success(result)
        
        # Verify we got exactly the requested batches
        result_ids = {batch.id for batch in result.data}
        assert result_ids == set(target_ids)
        assert len(result.data) == 3

    def test_filter_by_non_existent_id(self, client: TofuPilot):
        """Test filtering by non-existent ID returns empty result."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        result = client.batches.list(ids=[fake_id])
        assert_get_batches_success(result)
        assert len(result.data) == 0

    def test_filter_by_mixed_valid_invalid_ids(self, client: TofuPilot, test_batches_for_ids: List[models.BatchCreateResponse]):
        """Test filtering by mix of valid and invalid IDs."""
        valid_id = test_batches_for_ids[0].id
        invalid_id = "00000000-0000-0000-0000-000000000000"
        
        result = client.batches.list(ids=[valid_id, invalid_id])
        assert_get_batches_success(result)
        
        # Should only return the valid batch
        assert len(result.data) == 1
        assert result.data[0].id == valid_id

    def test_filter_by_all_test_ids(self, client: TofuPilot, test_batches_for_ids: List[models.BatchCreateResponse]):
        """Test filtering by all test batch IDs."""
        all_ids = [batch.id for batch in test_batches_for_ids]
        
        result = client.batches.list(ids=all_ids)
        assert_get_batches_success(result)
        
        # Should return all test batches
        result_ids = {batch.id for batch in result.data}
        assert result_ids == set(all_ids)
        assert len(result.data) == len(test_batches_for_ids)

    def test_ids_filter_with_pagination(self, client: TofuPilot, test_batches_for_ids: List[models.BatchCreateResponse]):
        """Test ID filtering combined with pagination."""
        target_ids = [batch.id for batch in test_batches_for_ids]
        
        # Get first page
        page1 = client.batches.list(ids=target_ids, limit=2)
        assert_get_batches_success(page1)
        assert len(page1.data) <= 2
        
        # Verify all results are from our target IDs
        for batch in page1.data:
            assert batch.id in target_ids

    def test_empty_ids_list(self, client: TofuPilot):
        """Test behavior with empty IDs list."""
        # Empty list should return all batches (no filtering)
        result = client.batches.list(ids=[])
        assert_get_batches_success(result)