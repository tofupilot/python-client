"""Simple test to verify nested search functionality for units."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot


class TestUnitsNestedSearchSimple:
    """Test that nested search is working on units."""

    def test_nested_search_functionality(self, client: TofuPilot):
        """Test that we can search units by nested fields without errors."""
        # Create test data: part, revision, batch, and unit
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"NESTED-SEARCH-PART-{timestamp}"
        part_name = f"Test Part for Nested Search {timestamp}"
        revision_number = f"REV-{timestamp}"
        batch_number = f"BATCH-{timestamp}"
        serial_number = f"UNIT-{timestamp}"
        
        # Create part with known number
        client.parts.create(
            number=part_number,
            name=part_name
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create batch for the part
        batch_result = client.batches.create(
            number=batch_number
        )
        
        # Create unit with this part, revision, and batch
        unit_result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number,
            batch_id=batch_result.id
        )
        
        # Test 1: Search by part number fragment
        part_number_fragment = "NESTED-SEARCH"
        search_results = client.units.list(search_query=part_number_fragment)
        assert isinstance(search_results.data, list)
            
        # Test 2: Search by batch number fragment
        batch_fragment = "BATCH"
        search_results = client.units.list(search_query=batch_fragment)
        assert isinstance(search_results.data, list)
                
        # Test 3: Search by revision number fragment
        revision_fragment = "REV"
        search_results = client.units.list(search_query=revision_fragment)
        assert isinstance(search_results.data, list)
                
        # Test 4: Search with a string that won't match any nested fields
        # This tests that the exists checks prevent crashes on null fields
        search_results = client.units.list(search_query="XYZNONEXISTENT123")
        assert isinstance(search_results.data, list)
        # Could be 0 results, but shouldn't crash
        
        # Test 5: Search by serial number still works
        serial_fragment = "UNIT"
        search_results = client.units.list(search_query=serial_fragment)
        assert isinstance(search_results.data, list)
        found_unit_ids = {u.id for u in search_results.data}
        assert unit_result.id in found_unit_ids, "Should find our unit when searching by serial number fragment"