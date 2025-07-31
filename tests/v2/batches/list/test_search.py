"""Test search functionality in batches.list()."""

import pytest
from typing import List, Tuple
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_batch_success, assert_get_batches_success


class TestBatchesSearch:
    """Test search parameter for partial text matching."""
    
    @pytest.fixture
    def test_batches_for_search(self, client: TofuPilot) -> List[tuple[models.BatchCreateResponse, str]]:
        """Create test batches with various patterns for search tests."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        
        test_configs = [
            f"PRODUCTION-LINE-A-{timestamp}",
            f"PRODUCTION-LINE-B-{timestamp}",
            f"QA-TESTING-BATCH-{timestamp}",
            f"EXPERIMENTAL-RUN-{timestamp}",
            f"SPECIAL-CHARS-123-{timestamp}",
            f"lowercase-batch-{timestamp}",
            f"MiXeD-CaSe-BaTcH-{timestamp}",
        ]
        
        test_batches: List[Tuple[models.BatchCreateResponse, str]] = []
        for batch_number in test_configs:
            batch = client.batches.create(number=batch_number)
            assert_create_batch_success(batch)
            test_batches.append((batch, batch_number))
            
        return test_batches

    def test_search_simple_term(self, client: TofuPilot, test_batches_for_search: List[tuple[models.BatchCreateResponse, str]]):
        """Test searching with a simple term."""
        result = client.batches.list(search_query="PRODUCTION")
        assert_get_batches_success(result)
        
        # Filter to only test batches
        test_batch_ids = {b.id for b, _ in test_batches_for_search}
        filtered_results = [b for b in result.data if b.id in test_batch_ids]
        
        # Should find batches containing "PRODUCTION"
        assert len(filtered_results) >= 2
        for batch in filtered_results:
            assert "PRODUCTION" in batch.number.upper()

    def test_search_case_insensitive(self, client: TofuPilot, test_batches_for_search: List[tuple[models.BatchCreateResponse, str]]):
        """Test that search is case-insensitive."""
        # Search lowercase for uppercase content
        result_lower = client.batches.list(search_query="production")
        assert_get_batches_success(result_lower)
        
        # Search uppercase for lowercase content
        result_upper = client.batches.list(search_query="LOWERCASE")
        assert_get_batches_success(result_upper)
        
        # Both should find matches
        test_batch_numbers = {number for _, number in test_batches_for_search}
        
        # Check lowercase search finds PRODUCTION batches
        production_found = any("PRODUCTION" in b.number for b in result_lower.data if b.number in test_batch_numbers)
        assert production_found
        
        # Check uppercase search finds lowercase batch
        lowercase_found = any("lowercase" in b.number for b in result_upper.data if b.number in test_batch_numbers)
        assert lowercase_found

    def test_search_partial_match(self, client: TofuPilot, test_batches_for_search: List[tuple[models.BatchCreateResponse, str]]):
        """Test partial string matching in search."""
        result = client.batches.list(search_query="LINE")
        assert_get_batches_success(result)
        
        # Filter to only test batches
        test_batch_ids = {b.id for b, _ in test_batches_for_search}
        filtered_results = [b for b in result.data if b.id in test_batch_ids]
        
        # Should find batches with "LINE" in them
        assert len(filtered_results) >= 2
        for batch in filtered_results:
            assert "LINE" in batch.number.upper()

    def test_search_special_characters(self, client: TofuPilot, test_batches_for_search: List[tuple[models.BatchCreateResponse, str]]):
        """Test searching with special characters (hyphens)."""
        result = client.batches.list(search_query="CHARS-123")
        assert_get_batches_success(result)
        
        # Check if special character batch is found
        test_batch_numbers = {number for _, number in test_batches_for_search}
        special_found = any("CHARS-123" in b.number for b in result.data if b.number in test_batch_numbers)
        assert special_found

    def test_search_no_results(self, client: TofuPilot):
        """Test search that returns no results."""
        result = client.batches.list(search_query="XYZNONEXISTENTXYZ")
        assert_get_batches_success(result)
        assert len(result.data) == 0

    def test_search_with_hyphen(self, client: TofuPilot, test_batches_for_search: List[tuple[models.BatchCreateResponse, str]]):
        """Test searching with hyphenated terms."""
        result = client.batches.list(search_query="LINE-A")
        assert_get_batches_success(result)
        
        # Should find the specific production line A batch
        test_batch_ids = {b.id for b, _ in test_batches_for_search}
        filtered_results = [b for b in result.data if b.id in test_batch_ids]
        
        assert any("LINE-A" in b.number for b in filtered_results)

    def test_search_with_filters(self, client: TofuPilot, test_batches_for_search: List[tuple[models.BatchCreateResponse, str]]):
        """Test combining search with other filters."""
        # Get a subset of test batch IDs
        subset_ids = [test_batches_for_search[0][0].id, test_batches_for_search[1][0].id]
        
        result = client.batches.list(
            ids=subset_ids,
            search_query="PRODUCTION"
        )
        assert_get_batches_success(result)
        
        # Should only return batches that match both criteria
        for batch in result.data:
            assert batch.id in subset_ids
            assert "PRODUCTION" in batch.number.upper()

    def test_search_with_pagination(self, client: TofuPilot, test_batches_for_search: List[tuple[models.BatchCreateResponse, str]]):
        """Test search combined with pagination."""
        result = client.batches.list(
            search_query="BATCH",
            limit=2
        )
        assert_get_batches_success(result)
        assert len(result.data) <= 2
        
        # All results should contain "BATCH"
        for batch in result.data:
            assert "BATCH" in batch.number.upper()

    def test_search_empty_string(self, client: TofuPilot):
        """Test behavior with empty search string."""
        # Empty search should return all batches (no filtering)
        result = client.batches.list(search_query="", limit=5)
        assert_get_batches_success(result)