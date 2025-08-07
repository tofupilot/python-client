"""Test sorting parameters in batches.list()."""

import pytest
from typing import List, Tuple, cast
from datetime import datetime, timezone
import time
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_batch_success, assert_get_batches_success


class TestBatchesSorting:
    """Test sort_by and sort_order parameters."""
    
    @pytest.fixture
    def test_batches_sorted_data(self, client: TofuPilot, timestamp) -> List[models.BatchCreateResponse]:
        """Create test batches with different timestamps and numbers for sorting tests."""
        
        test_batches: List[models.BatchCreateResponse] = []
        # Create batches with different numbers and slight time delays
        batch_configs: List[Tuple[str, float]] = [
            ("SORT-AAA", 0),
            ("SORT-CCC", 0.1),
            ("SORT-BBB", 0.2),
            ("SORT-DDD", 0.3),
            ("SORT-EEE", 0.4),
        ]
        
        for batch_suffix, delay in batch_configs:
            if delay > 0:
                time.sleep(delay)  # Small delay to ensure different timestamps
            
            batch = client.batches.create(
                number=f"{batch_suffix}-{timestamp}"
            )
            assert_create_batch_success(batch)
            test_batches.append(batch)
            
        return test_batches

    def test_sort_by_created_at_desc(self, client: TofuPilot, test_batches_sorted_data: List[models.BatchCreateResponse]):
        """Test sorting by created_at in descending order (newest first)."""
        test_batch_ids = [batch.id for batch in test_batches_sorted_data]
        
        result = client.batches.list(
            ids=test_batch_ids,
            sort_by="created_at",
            sort_order="desc"
        )
        assert_get_batches_success(result)
        
        # Verify descending order by created_at
        for i in range(len(result.data) - 1):
            assert result.data[i].created_at >= result.data[i + 1].created_at

    def test_sort_by_created_at_asc(self, client: TofuPilot, test_batches_sorted_data: List[models.BatchCreateResponse]):
        """Test sorting by created_at in ascending order (oldest first)."""
        test_batch_ids = [batch.id for batch in test_batches_sorted_data]
        
        result = client.batches.list(
            ids=test_batch_ids,
            sort_by="created_at",
            sort_order="asc"
        )
        assert_get_batches_success(result)
        
        # Verify ascending order by created_at
        for i in range(len(result.data) - 1):
            assert result.data[i].created_at <= result.data[i + 1].created_at

    def test_sort_by_number_desc(self, client: TofuPilot, test_batches_sorted_data: List[models.BatchCreateResponse]):
        """Test sorting by number in descending order."""
        test_batch_ids = [batch.id for batch in test_batches_sorted_data]
        
        result = client.batches.list(
            ids=test_batch_ids,
            sort_by="number",
            sort_order="desc"
        )
        assert_get_batches_success(result)
        
        # Verify descending order by number
        for i in range(len(result.data) - 1):
            assert result.data[i].number >= result.data[i + 1].number

    def test_sort_by_number_asc(self, client: TofuPilot, test_batches_sorted_data: List[models.BatchCreateResponse]):
        """Test sorting by number in ascending order."""
        test_batch_ids = [batch.id for batch in test_batches_sorted_data]
        
        result = client.batches.list(
            ids=test_batch_ids,
            sort_by="number",
            sort_order="asc"
        )
        assert_get_batches_success(result)
        
        # Verify ascending order by number
        for i in range(len(result.data) - 1):
            assert result.data[i].number <= result.data[i + 1].number

    def test_default_sorting(self, client: TofuPilot):
        """Test default sorting behavior (should be created_at desc)."""
        result = client.batches.list(limit=10)
        assert_get_batches_success(result)
        
        # Default should be newest first (created_at desc)
        if len(result.data) > 1:
            for i in range(len(result.data) - 1):
                assert result.data[i].created_at >= result.data[i + 1].created_at

    def test_sorting_with_pagination(self, client: TofuPilot, test_batches_sorted_data: List[models.BatchCreateResponse]):
        """Test that sorting is maintained across paginated results."""
        test_batch_ids = [batch.id for batch in test_batches_sorted_data]
        
        # Get first page sorted by number
        page1 = client.batches.list(
            ids=test_batch_ids,
            sort_by="number",
            sort_order="asc",
            limit=2
        )
        assert_get_batches_success(page1)
        
        if hasattr(page1, 'meta') and hasattr(page1.meta, 'next_cursor') and page1.meta.next_cursor:
            # Get second page
            page2 = client.batches.list(
                ids=test_batch_ids,
                sort_by="number",
                sort_order="asc",
                limit=2,
                cursor=cast(int, page1.meta.next_cursor)
            )
            assert_get_batches_success(page2)
            
            # Verify sorting is maintained across pages
            if page1.data and page2.data:
                last_of_page1 = page1.data[-1].number
                first_of_page2 = page2.data[0].number
                assert last_of_page1 <= first_of_page2