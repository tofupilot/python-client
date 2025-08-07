"""Test batches search functionality."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_batch_success, assert_get_batches_success


class TestBatchesSearch:
    """Test batches search functionality with independent test data."""

    def test_basic_search_functionality(self, client: TofuPilot, timestamp: str):
        """Test basic search functionality works."""
        # Create test batches
        
        batch1_number = f"SEARCH-TEST-ALPHA-{timestamp}"
        batch2_number = f"SEARCH-TEST-BETA-{timestamp}"
        batch3_number = f"DIFFERENT-NAME-{timestamp}"
        
        batch1 = client.batches.create(number=batch1_number)
        batch2 = client.batches.create(number=batch2_number)
        batch3 = client.batches.create(number=batch3_number)
        
        assert_create_batch_success(batch1)
        assert_create_batch_success(batch2)
        assert_create_batch_success(batch3)
        
        # Test search by common prefix
        results = client.batches.list(search_query="SEARCH-TEST", limit=10)
        assert_get_batches_success(results)
        
        found_ids = {batch.id for batch in results.data}
        assert batch1.id in found_ids
        assert batch2.id in found_ids
        # batch3 should not be found as it doesn't match "SEARCH-TEST" prefix
        
        # Test exact number search
        results = client.batches.list(search_query=batch1_number, limit=10)
        assert_get_batches_success(results)
        assert len(results.data) >= 1
        assert batch1.id in {batch.id for batch in results.data}
        
        # Test partial number search
        results = client.batches.list(search_query="ALPHA", limit=10)
        assert_get_batches_success(results)
        found_ids = {batch.id for batch in results.data}
        assert batch1.id in found_ids

    def test_empty_search(self, client: TofuPilot):
        """Test empty search returns results without error."""
        results = client.batches.list(search_query="", limit=5)
        assert_get_batches_success(results)
        assert isinstance(results.data, list)

    def test_nonexistent_search(self, client: TofuPilot):
        """Test search for non-existent term returns empty results."""
        results = client.batches.list(search_query="DEFINITELY_NONEXISTENT_XYZ123", limit=5)
        assert_get_batches_success(results)
        assert isinstance(results.data, list)
        # Results can be empty or contain unrelated batches, both are valid

    def test_search_with_special_characters(self, client: TofuPilot, timestamp: str):
        """Test search works with batches containing special characters."""
        
        special_batch_number = f"SPECIAL_TEST-{timestamp}"
        batch = client.batches.create(number=special_batch_number)
        assert_create_batch_success(batch)
        
        # Search should work with special characters
        results = client.batches.list(search_query="SPECIAL", limit=10)
        assert_get_batches_success(results)
        
        found_ids = {b.id for b in results.data}
        assert batch.id in found_ids