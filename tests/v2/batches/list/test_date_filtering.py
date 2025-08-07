"""Test date-based filtering in batches.list()."""

import pytest
from typing import List
from datetime import datetime, timezone, timedelta
import time
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_batch_success, assert_get_batches_success


class TestBatchesDateFiltering:
    """Test filtering batches by creation date ranges."""
    
    @pytest.fixture
    def test_batches_with_dates(self, client: TofuPilot, timestamp) -> List[models.BatchCreateResponse]:
        """Create test batches at different times for date filtering tests."""
        
        test_batches: List[models.BatchCreateResponse] = []
        # Create batches with small delays to ensure different timestamps
        for i in range(5):
            batch = client.batches.create(
                number=f"DATE-FILTER-{timestamp}-{i:03d}"
            )
            assert_create_batch_success(batch)
            test_batches.append(batch)
            if i < 4:  # Small delay between batches except the last one
                time.sleep(0.1)
            
        return test_batches

    def test_filter_by_created_after(self, client: TofuPilot, test_batches_with_dates: List[models.BatchCreateResponse]):
        """Test filtering batches created after a specific date."""
        # Use the creation time of the middle batch as threshold
        middle_batch = test_batches_with_dates[2]
        # Fetch batch details to get created_at
        batch_details = client.batches.list(ids=[middle_batch.id])
        assert len(batch_details.data) == 1
        threshold_time = batch_details.data[0].created_at
        
        result = client.batches.list(
            created_after=threshold_time - timedelta(seconds=1)  # Slightly before to include it
        )
        assert_get_batches_success(result)
        
        # Filter test batches to only those we expect
        test_batch_ids = {b.id for b in test_batches_with_dates}
        filtered_results = [b for b in result.data if b.id in test_batch_ids]
        
        # Should include middle batch and all after it
        assert len(filtered_results) >= 3  # batches 2, 3, 4

    def test_filter_by_created_before(self, client: TofuPilot, test_batches_with_dates: List[models.BatchCreateResponse]):
        """Test filtering batches created before a specific date."""
        # Use the creation time of the middle batch as threshold
        middle_batch = test_batches_with_dates[2]
        # Fetch batch details to get created_at
        batch_details = client.batches.list(ids=[middle_batch.id])
        assert len(batch_details.data) == 1
        threshold_time = batch_details.data[0].created_at
        
        result = client.batches.list(
            created_before=threshold_time + timedelta(seconds=1)  # Slightly after to include it
        )
        assert_get_batches_success(result)
        
        # Filter test batches to only those we expect
        test_batch_ids = {b.id for b in test_batches_with_dates}
        filtered_results = [b for b in result.data if b.id in test_batch_ids]
        
        # Should include middle batch and all before it
        assert len(filtered_results) >= 3  # batches 0, 1, 2

    def test_filter_by_date_range(self, client: TofuPilot, test_batches_with_dates: List[models.BatchCreateResponse]):
        """Test filtering batches within a date range."""
        # Get time range from second to fourth batch
        batch_details = client.batches.list(ids=[test_batches_with_dates[1].id, test_batches_with_dates[3].id])
        assert len(batch_details.data) == 2
        # Sort by created_at to ensure correct order
        sorted_batches = sorted(batch_details.data, key=lambda b: b.created_at)
        start_time = sorted_batches[0].created_at
        end_time = sorted_batches[1].created_at
        
        result = client.batches.list(
            created_after=start_time - timedelta(seconds=1),
            created_before=end_time + timedelta(seconds=1)
        )
        assert_get_batches_success(result)
        
        # Filter to only test batches
        test_batch_ids = {b.id for b in test_batches_with_dates}
        filtered_results = [b for b in result.data if b.id in test_batch_ids]
        
        # Should include batches 1, 2, 3
        assert len(filtered_results) >= 3

    def test_filter_by_future_date(self, client: TofuPilot):
        """Test filtering by future date returns no results."""
        future_date = datetime.now(timezone.utc) + timedelta(days=365)
        
        result = client.batches.list(created_after=future_date)
        assert_get_batches_success(result)
        assert len(result.data) == 0

    def test_filter_by_past_date(self, client: TofuPilot):
        """Test filtering by very old date returns results."""
        past_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        
        result = client.batches.list(created_after=past_date, limit=5)
        assert_get_batches_success(result)
        # Should return some results (up to limit)

    def test_narrow_date_range(self, client: TofuPilot, test_batches_with_dates: List[models.BatchCreateResponse]):
        """Test filtering with a very narrow date range."""
        target_batch = test_batches_with_dates[2]
        # Fetch batch details to get created_at
        batch_details = client.batches.list(ids=[target_batch.id])
        assert len(batch_details.data) == 1
        batch_time = batch_details.data[0].created_at
        
        # Create a 2-second window around the batch
        result = client.batches.list(
            created_after=batch_time - timedelta(seconds=1),
            created_before=batch_time + timedelta(seconds=1)
        )
        assert_get_batches_success(result)
        
        # Should include at least the target batch
        batch_ids = {b.id for b in result.data}
        assert target_batch.id in batch_ids

    def test_date_filter_with_pagination(self, client: TofuPilot, test_batches_with_dates: List[models.BatchCreateResponse]):
        """Test date filtering combined with pagination."""
        # Use all test batches time range
        batch_details = client.batches.list(ids=[test_batches_with_dates[0].id, test_batches_with_dates[-1].id])
        assert len(batch_details.data) == 2
        # Sort by created_at to ensure correct order
        sorted_batches = sorted(batch_details.data, key=lambda b: b.created_at)
        start_time = sorted_batches[0].created_at
        end_time = sorted_batches[1].created_at
        
        result = client.batches.list(
            created_after=start_time - timedelta(seconds=1),
            created_before=end_time + timedelta(seconds=1),
            limit=2
        )
        assert_get_batches_success(result)
        assert len(result.data) <= 2

    def test_date_filter_with_sorting(self, client: TofuPilot, test_batches_with_dates: List[models.BatchCreateResponse]):
        """Test date filtering combined with sorting."""
        # Use a date range that includes test batches
        batch_details = client.batches.list(ids=[test_batches_with_dates[0].id])
        assert len(batch_details.data) == 1
        start_time = batch_details.data[0].created_at
        
        result = client.batches.list(
            created_after=start_time - timedelta(seconds=1),
            sort_by="created_at",
            sort_order="asc",
            limit=10
        )
        assert_get_batches_success(result)
        
        # Verify ascending order
        for i in range(len(result.data) - 1):
            assert result.data[i].created_at <= result.data[i + 1].created_at