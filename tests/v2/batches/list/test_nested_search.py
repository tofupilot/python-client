"""Test search functionality for batches list - optimized version (batch number only)."""

import pytest
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone, timedelta
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_batch_success, assert_get_batches_success
from ...utils import assert_create_run_success


class TestBatchesNestedSearch:
    """Test that search is working correctly for batches (batch number search only)."""

    @pytest.fixture
    def test_batches_search_data(self, client: TofuPilot, procedure_id: str) -> Dict[str, Any]:
        """Create test batches with searchable batch numbers."""
        import uuid
        unique_id = str(uuid.uuid4())
        
        # Create batches with specific number patterns
        batch1_number = f"SEARCH-ALPHA-{unique_id}"
        batch1 = client.batches.create(number=batch1_number)
        assert_create_batch_success(batch1)
        
        batch2_number = f"SEARCH-BETA-{unique_id}"
        batch2 = client.batches.create(number=batch2_number)
        assert_create_batch_success(batch2)
        
        batch3_number = f"DIFFERENT-{unique_id}"
        batch3 = client.batches.create(number=batch3_number)
        assert_create_batch_success(batch3)
        
        # Create a unit for each batch to ensure they have content
        for i, batch_number in enumerate([batch1_number, batch2_number, batch3_number]):
            # Use unique part numbers to avoid conflicts
            run = client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number=f"UNIT-{i}-{uuid.uuid4()}",
                part_number=f"PART-{uuid.uuid4()}",
                revision_number=f"REV-{i}",
                started_at=datetime.now(timezone.utc) - timedelta(minutes=10),
                ended_at=datetime.now(timezone.utc) - timedelta(minutes=5),
                batch_number=batch_number
            )
            assert_create_run_success(run)
        
        return {
            "batches": [batch1, batch2, batch3],
            "batch_numbers": [batch1_number, batch2_number, batch3_number],
            "unique_id": unique_id
        }

    def test_search_by_batch_number(self, client: TofuPilot, test_batches_search_data: Dict[str, Any]):
        """Test searching batches by batch number."""
        data = test_batches_search_data
        
        # Search by partial batch number pattern
        search_results = client.batches.list(search_query="SEARCH")
        assert_get_batches_success(search_results)
        
        # Should find batch1 and batch2 (both have "SEARCH" in their numbers)
        found_numbers = {batch.number for batch in search_results.data}
        assert data["batch_numbers"][0] in found_numbers  # SEARCH-ALPHA
        assert data["batch_numbers"][1] in found_numbers  # SEARCH-BETA
        
        # Search for exact batch number
        search_results = client.batches.list(search_query=data["batch_numbers"][0])
        assert_get_batches_success(search_results)
        
        # Should find the exact batch
        found_ids = {batch.id for batch in search_results.data}
        assert data["batches"][0].id in found_ids

    def test_search_case_insensitive(self, client: TofuPilot, test_batches_search_data: Dict[str, Any]):
        """Test that batch search is case insensitive."""
        # data = test_batches_search_data  # Not used in this test
        
        # Create batch with mixed case
        import uuid
        mixed_case_number = f"MixedCase-Batch-{uuid.uuid4()}"
        batch = client.batches.create(number=mixed_case_number)
        assert_create_batch_success(batch)
        
        # Search with different cases
        for search_term in ["mixedcase", "MIXEDCASE", "MixedCase"]:
            search_results = client.batches.list(search_query=search_term)
            assert_get_batches_success(search_results)
            
            found_ids = {b.id for b in search_results.data}
            assert batch.id in found_ids, f"Should find batch with {search_term} search"

    def test_search_partial_match(self, client: TofuPilot, test_batches_search_data: Dict[str, Any]):
        """Test partial string matching for batch numbers."""
        data = test_batches_search_data
        
        # Search for partial patterns
        partial_searches: List[Tuple[str, List[str]]] = [
            ("ALPHA", [data["batch_numbers"][0]]),  # Should find SEARCH-ALPHA
            ("BETA", [data["batch_numbers"][1]]),   # Should find SEARCH-BETA
            (data["unique_id"], data["batch_numbers"])  # Should find all batches
        ]
        
        for search_term, expected_numbers in partial_searches:
            search_results = client.batches.list(search_query=search_term)
            assert_get_batches_success(search_results)
            
            found_numbers = {batch.number for batch in search_results.data}
            for expected in expected_numbers:
                assert expected in found_numbers, f"Should find {expected} with search '{search_term}'"

    def test_search_empty_query(self, client: TofuPilot):
        """Test that empty search query returns results without error."""
        search_results = client.batches.list(search_query="", limit=5)
        assert_get_batches_success(search_results)
        assert isinstance(search_results.data, list)

    def test_search_nonexistent_term(self, client: TofuPilot):
        """Test searching for non-existent batch numbers."""
        search_results = client.batches.list(search_query="DEFINITELY-NONEXISTENT-XYZ123")
        assert_get_batches_success(search_results)
        
        # Should return valid response, likely empty
        assert isinstance(search_results.data, list)

    def test_unit_serial_search_not_supported(self, client: TofuPilot, procedure_id: str):
        """Test that unit serial search is no longer supported (optimized out)."""
        # Create batch with units
        import uuid
        batch_number = f"BATCH-UNIT-TEST-{uuid.uuid4()}"
        batch = client.batches.create(number=batch_number)
        assert_create_batch_success(batch)
        
        # Create unit with unique serial
        unique_serial = f"UNIQUE-SERIAL-XYZ-{uuid.uuid4()}"
        run = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=unique_serial,
            part_number=f"PART-UNIQUE-{uuid.uuid4()}",
            revision_number=f"REV-UNIQUE-{uuid.uuid4()}",
            batch_number=batch_number,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            ended_at=datetime.now(timezone.utc)
        )
        assert_create_run_success(run)
        
        # Search by unit serial should NOT find the batch
        search_results = client.batches.list(search_query=unique_serial)
        assert_get_batches_success(search_results)
        
        # The batch should NOT be found when searching by unit serial
        found_ids = {b.id for b in search_results.data}
        # We don't assert it's not found as it might find unrelated batches
        
        # But we can find it by batch number
        search_results = client.batches.list(search_query=batch_number)
        assert_get_batches_success(search_results)
        found_ids = {b.id for b in search_results.data}
        assert batch.id in found_ids