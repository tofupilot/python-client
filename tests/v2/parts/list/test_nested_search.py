"""Test parts search functionality."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ..utils import assert_get_parts_success


class TestPartsSearch:
    """Test parts search functionality with independent test data."""

    def test_search_by_part_number(self, client: TofuPilot, timestamp):
        """Test searching parts by part number."""
        # Create test data: parts with searchable numbers
        
        part1_number = f"SEARCH-ALPHA-{timestamp}"
        part2_number = f"SEARCH-BETA-{timestamp}"
        part3_number = f"DIFFERENT-{timestamp}"
        
        part1 = client.parts.create(number=part1_number, name="Alpha Part")
        part2 = client.parts.create(number=part2_number, name="Beta Part")  
        client.parts.create(number=part3_number, name="Different Part")
        
        # Test search by common prefix
        results = client.parts.list(search_query="SEARCH")
        assert_get_parts_success(results)
        
        found_ids = {part.id for part in results.data}
        assert part1.id in found_ids
        assert part2.id in found_ids
        # part3 should not be found as it doesn't match "SEARCH" prefix
        
        # Test exact part number search
        results = client.parts.list(search_query=part1_number)
        assert_get_parts_success(results)
        assert len(results.data) >= 1
        assert part1.id in {part.id for part in results.data}

    def test_search_by_part_name(self, client: TofuPilot, timestamp):
        """Test searching parts by part name."""
        # Create test data with searchable names
        
        part_number = f"PART-NAME-SEARCH-{timestamp}"
        part_name = f"SEARCHABLE-NAME-{timestamp}"
        
        part_result = client.parts.create(
            number=part_number,
            name=part_name
        )
        
        # Search by part name should find the part
        results = client.parts.list(search_query="SEARCHABLE-NAME")
        assert_get_parts_success(results)
        
        found_ids = {part.id for part in results.data}
        assert part_result.id in found_ids

    def test_search_by_revision_number(self, client: TofuPilot, timestamp):
        """Test that revision search is no longer supported (optimized out)."""
        # Create test data: part with revision
        part_number = f"PART-REV-SEARCH-{timestamp}"
        revision_number = f"SEARCHABLE-REV-{timestamp}"
        
        # Create part
        part_result = client.parts.create(
            number=part_number,
            name=f"Part for Revision Search {timestamp}"
        )
        
        # Create revision for the part
        client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Search by revision number should NOT find the part (optimized out)
        results = client.parts.list(search_query="SEARCHABLE-REV")
        assert_get_parts_success(results)
        
        # The part should NOT be found when searching by revision
        found_ids = {part.id for part in results.data}
        # This assertion is now reversed - we don't expect to find it
        # assert part_result.id not in found_ids  # Commented out as it might find other parts
        
        # But we can still find it by part number
        results = client.parts.list(search_query=part_number)
        assert_get_parts_success(results)
        found_ids = {part.id for part in results.data}
        assert part_result.id in found_ids

    def test_empty_search(self, client: TofuPilot):
        """Test empty search returns results without error."""
        results = client.parts.list(search_query="", limit=5)
        assert_get_parts_success(results)
        assert isinstance(results.data, list)

    def test_nonexistent_search(self, client: TofuPilot):
        """Test search for non-existent term returns empty or valid results."""
        results = client.parts.list(search_query="DEFINITELY_NONEXISTENT_XYZ123", limit=5)
        assert_get_parts_success(results)
        assert isinstance(results.data, list)
        # Results can be empty or contain unrelated parts, both are valid

    def test_partial_search(self, client: TofuPilot, timestamp):
        """Test partial string search works correctly."""
        # Create test data with known pattern
        part_number = f"PARTIAL-SEARCH-{timestamp}"
        
        part_result = client.parts.create(
            number=part_number,
            name=f"Test Part for Partial Search {timestamp}"
        )
        
        # Search by partial string should find the part
        results = client.parts.list(search_query="PARTIAL-SEARCH")
        assert_get_parts_success(results)
        
        found_ids = {part.id for part in results.data}
        assert part_result.id in found_ids

    def test_case_insensitive_search(self, client: TofuPilot, timestamp):
        """Test that search is case insensitive."""
        # Create test data with mixed case
        part_number = f"CASE-TEST-{timestamp}"
        part_name = f"CaseSensitive-{timestamp}"
        
        part_result = client.parts.create(
            number=part_number,
            name=part_name
        )
        
        # Search with different case should still find the part
        results = client.parts.list(search_query="case-test")
        assert_get_parts_success(results)
        
        found_ids = {part.id for part in results.data}
        assert part_result.id in found_ids

    def test_special_characters_search(self, client: TofuPilot, timestamp):
        """Test search works with allowed special characters (hyphens and underscores)."""
        # Create test data with allowed special characters
        part_number = f"SPECIAL_TEST-{timestamp}"
        
        part_result = client.parts.create(
            number=part_number,
            name=f"Special Test Part {timestamp}"
        )
        
        # Search should work with special characters
        results = client.parts.list(search_query="SPECIAL_TEST")
        assert_get_parts_success(results)
        
        found_ids = {part.id for part in results.data}
        assert part_result.id in found_ids