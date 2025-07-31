"""Test number-based filtering in batches.list()."""

import pytest
from typing import List, Tuple
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_batch_success, assert_get_batches_success


class TestBatchesNumbersFiltering:
    """Test filtering batches by numbers."""
    
    @pytest.fixture
    def test_batches_for_numbers(self, client: TofuPilot) -> List[tuple[models.BatchCreateResponse, str]]:
        """Create test batches with specific numbers for filtering tests."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        
        test_configs = [
            f"BATCH-ALPHA-{timestamp}",
            f"BATCH-BETA-{timestamp}",
            f"BATCH-GAMMA-{timestamp}",
            f"BATCH-DELTA-{timestamp}",
            f"BATCH-EPSILON-{timestamp}",
        ]
        
        test_batches: List[Tuple[models.BatchCreateResponse, str]] = []
        for batch_number in test_configs:
            batch = client.batches.create(number=batch_number)
            assert_create_batch_success(batch)
            test_batches.append((batch, batch_number))
            
        return test_batches

    def test_filter_by_single_number(self, client: TofuPilot, test_batches_for_numbers: List[tuple[models.BatchCreateResponse, str]]):
        """Test filtering by a single batch number."""
        target_batch, target_number = test_batches_for_numbers[0]
        
        result = client.batches.list(numbers=[target_number])
        assert_get_batches_success(result)
        
        assert len(result.data) == 1
        assert result.data[0].id == target_batch.id
        assert result.data[0].number == target_number

    def test_filter_by_multiple_numbers(self, client: TofuPilot, test_batches_for_numbers: List[tuple[models.BatchCreateResponse, str]]):
        """Test filtering by multiple batch numbers."""
        target_numbers = [
            test_batches_for_numbers[0][1],
            test_batches_for_numbers[2][1],
            test_batches_for_numbers[4][1]
        ]
        
        result = client.batches.list(numbers=target_numbers)
        assert_get_batches_success(result)
        
        # Verify we got exactly the requested batches
        result_numbers = {batch.number for batch in result.data}
        assert result_numbers == set(target_numbers)
        assert len(result.data) == 3

    def test_filter_by_non_existent_number(self, client: TofuPilot):
        """Test filtering by non-existent number returns empty result."""
        fake_number = "NON-EXISTENT-BATCH-999999"
        
        result = client.batches.list(numbers=[fake_number])
        assert_get_batches_success(result)
        assert len(result.data) == 0

    def test_filter_by_partial_number_no_match(self, client: TofuPilot, test_batches_for_numbers: List[tuple[models.BatchCreateResponse, str]]):
        """Test that partial numbers don't match (exact match required)."""
        # Try partial number
        partial_number = "BATCH-ALPHA"  # Missing timestamp part
        
        result = client.batches.list(numbers=[partial_number])
        assert_get_batches_success(result)
        assert len(result.data) == 0  # Should not match partially

    def test_filter_case_insensitive(self, client: TofuPilot, test_batches_for_numbers: List[tuple[models.BatchCreateResponse, str]]):
        """Test that number filtering is case-insensitive."""
        batch_resp, original_number = test_batches_for_numbers[0]
        lowercase_number = original_number.lower()
        
        # Search with lowercase version
        result = client.batches.list(numbers=[lowercase_number])
        assert_get_batches_success(result)
        
        # Should match if case-insensitive (API matches case-insensitively)
        if original_number != lowercase_number:
            assert len(result.data) == 1
            assert result.data[0].id == batch_resp.id
            assert result.data[0].number == original_number  # Returns original case

    def test_filter_by_all_test_numbers(self, client: TofuPilot, test_batches_for_numbers: List[tuple[models.BatchCreateResponse, str]]):
        """Test filtering by all test batch numbers."""
        all_numbers = [number for _, number in test_batches_for_numbers]
        
        result = client.batches.list(numbers=all_numbers)
        assert_get_batches_success(result)
        
        # Should return all test batches
        result_numbers = {batch.number for batch in result.data}
        assert result_numbers == set(all_numbers)
        assert len(result.data) == len(test_batches_for_numbers)

    def test_numbers_filter_with_sorting(self, client: TofuPilot, test_batches_for_numbers: List[tuple[models.BatchCreateResponse, str]]):
        """Test number filtering combined with sorting."""
        target_numbers = [number for _, number in test_batches_for_numbers]
        
        result = client.batches.list(
            numbers=target_numbers,
            sort_by="number",
            sort_order="asc"
        )
        assert_get_batches_success(result)
        
        # Verify results are sorted
        for i in range(len(result.data) - 1):
            assert result.data[i].number <= result.data[i + 1].number

    def test_empty_numbers_list(self, client: TofuPilot):
        """Test behavior with empty numbers list."""
        # Empty list should return all batches (no filtering)
        result = client.batches.list(numbers=[])
        assert_get_batches_success(result)

    def test_combine_ids_and_numbers_filters(self, client: TofuPilot, test_batches_for_numbers: List[tuple[models.BatchCreateResponse, str]]):
        """Test combining IDs and numbers filters (should be OR operation)."""
        # Pick one batch by ID and another by number
        batch_by_id, _ = test_batches_for_numbers[0]
        batch_by_number, number_by_number = test_batches_for_numbers[1]
        
        result = client.batches.list(
            ids=[batch_by_id.id],
            numbers=[number_by_number]
        )
        assert_get_batches_success(result)
        
        # Should return both batches (OR operation)
        result_ids = {batch.id for batch in result.data}
        assert batch_by_id.id in result_ids
        assert batch_by_number.id in result_ids
        assert len(result.data) >= 2