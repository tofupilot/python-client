"""Test parts list search functionality."""

from datetime import datetime, timezone
from typing import List, Tuple, Optional
import pytest
import uuid
from tofupilot.v2 import TofuPilot
from tofupilot.v2.models.part_createop import PartCreateResponse
from ..utils import assert_create_part_success, assert_get_parts_success


class TestPartsListSearch:
    """Test parts list search functionality."""
    
    @pytest.fixture
    def test_parts_for_search(self, client: TofuPilot, auth_type: str) -> List[PartCreateResponse]:
        """Create test parts for search tests."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        created_parts: List[PartCreateResponse] = []
        
        # Create parts with different patterns
        test_parts: List[Tuple[str, str, Optional[str]]] = [
            # (number, name, revision_number)
            (f"SEARCH-ABC-{timestamp}-{unique_id}", "Alpha Component", "REV-1"),
            (f"SEARCH-DEF-{timestamp}-{unique_id}", "Beta Device", "REV-2"),
            (f"SEARCH-XYZ-{timestamp}-{unique_id}", "Gamma Module ABC", None),
            (f"TEST-{timestamp}-{unique_id}-UNIQUE", "Unique Part Name", "REV-ABC"),
            (f"MOTOR-{timestamp}-{unique_id}", "Motor Controller", "REV-A"),
            (f"SENSOR-{timestamp}-{unique_id}", "Temperature Sensor ABC", None),
        ]
        
        for part_number, part_name, revision_number in test_parts:
            if revision_number:
                result = client.parts.create(
                    number=part_number,
                    name=part_name,
                    revision_number=revision_number
                )
            else:
                result = client.parts.create(
                    number=part_number,
                    name=part_name
                )
            assert_create_part_success(result)
            created_parts.append(result)
        
        return created_parts
    
    def test_search_by_part_number(self, client: TofuPilot, test_parts_for_search: List[PartCreateResponse]) -> None:
        """Test searching parts by part number."""
        # Create a unique search term for this test
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        unique_search_term = f"SEARCHNUM-{timestamp}"
        
        # Create parts with this unique search term
        created_ids: List[str] = []
        for i in range(3):
            result = client.parts.create(
                number=f"{unique_search_term}-{i}",
                name=f"Test Part {i}"
            )
            assert_create_part_success(result)
            created_ids.append(result.id)
        
        # Search for our unique term
        result = client.parts.list(search_query=unique_search_term)
        assert_get_parts_success(result)
        
        # Should find exactly our 3 parts
        assert len(result.data) == 3
        
        # Verify all results are our parts
        found_ids = {p.id for p in result.data}
        assert found_ids == set(created_ids)
    
    def test_search_by_part_name(self, client: TofuPilot, test_parts_for_search: List[PartCreateResponse]) -> None:
        """Test searching parts by name."""
        # Create a unique search term for this test
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        unique_name_term = f"UniqueComponent-{timestamp}"
        
        # Create a part with this unique name
        result = client.parts.create(
            number=f"NAMETEST-{timestamp}",
            name=unique_name_term
        )
        assert_create_part_success(result)
        created_id = result.id
        
        # Search for our unique term
        result = client.parts.list(search_query=unique_name_term)
        assert_get_parts_success(result)
        
        # Should find exactly our part
        assert len(result.data) == 1
        assert result.data[0].id == created_id
        assert unique_name_term in result.data[0].name
    
    
    def test_search_case_insensitive(self, client: TofuPilot, test_parts_for_search: List[PartCreateResponse]) -> None:
        """Test that search is case-insensitive."""
        # Search with different cases
        searches = ["motor", "MOTOR", "MoToR"]
        
        results: List[int] = []
        for search_term in searches:
            result = client.parts.list(search_query=search_term)
            assert_get_parts_success(result)
            results.append(len(result.data))
        
        # All searches should return the same number of results
        assert all(r == results[0] for r in results)
        assert results[0] >= 1  # Should find at least the Motor Controller
    
    def test_search_partial_match(self, client: TofuPilot, test_parts_for_search: List[PartCreateResponse]) -> None:
        """Test partial string matching in search."""
        # Search for "ABC" which appears in multiple places
        result = client.parts.list(search_query="ABC")
        assert_get_parts_success(result)
        
        # Should find multiple parts:
        # - SEARCH-ABC (in number)
        # - Gamma Module ABC (in name)
        # - Temperature Sensor ABC (in name)
        # - REV-ABC (in revision)
        assert len(result.data) >= 3
    
    def test_search_empty_query(self, client: TofuPilot) -> None:
        """Test that empty search query returns all parts."""
        # Get all parts
        all_parts = client.parts.list()
        assert_get_parts_success(all_parts)
        
        # Get parts with empty search
        empty_search = client.parts.list(search_query="")
        assert_get_parts_success(empty_search)
        
        # Should return the same results
        assert len(all_parts.data) == len(empty_search.data)
    
    def test_search_no_results(self, client: TofuPilot) -> None:
        """Test search that returns no results."""
        # Search for something that shouldn't exist
        unique_string = f"NONEXISTENT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        result = client.parts.list(search_query=unique_string)
        assert_get_parts_success(result)
        
        # Should return empty list
        assert len(result.data) == 0
        assert result.meta.has_more is False
    
    def test_search_special_characters(self, client: TofuPilot, test_parts_for_search: List[PartCreateResponse]) -> None:
        """Test search with special characters."""
        # Search for hyphenated terms
        result = client.parts.list(search_query="SEARCH-ABC")
        assert_get_parts_success(result)
        
        # Should find the exact match
        assert len(result.data) >= 1
        
        # Search with spaces
        result_spaces = client.parts.list(search_query="Unique Part")
        assert_get_parts_success(result_spaces)
        assert len(result_spaces.data) >= 1
    
    def test_search_by_revision_number(self, client: TofuPilot, test_parts_for_search: List[PartCreateResponse]) -> None:
        """Test searching parts by revision number."""
        # Create a unique revision number for this test
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        unique_revision = f"REV-{timestamp}"
        
        # Create a part with this unique revision
        result = client.parts.create(
            number=f"REVTEST-{timestamp}",
            name=f"Revision Test Part {timestamp}",
            revision_number=unique_revision
        )
        assert_create_part_success(result)
        created_id = result.id
        
        # Search for our unique revision number
        result = client.parts.list(search_query=unique_revision)
        assert_get_parts_success(result)
        
        # Should find exactly our part
        assert len(result.data) == 1
        assert result.data[0].id == created_id
        
        # Verify the part has the revision we searched for
        found_part = result.data[0]
        revision_numbers = [rev.number for rev in found_part.revisions]
        assert unique_revision in revision_numbers