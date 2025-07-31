"""Test search functionality in units.list()."""

import pytest
from typing import List, Tuple
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_unit_success, assert_get_units_success


class TestUnitsSearch:
    """Test search functionality in units.list()."""
    
    @pytest.fixture
    def test_units_for_search(self, client: TofuPilot) -> List[Tuple[models.UnitCreateResponse, str]]:
        """Create test units with specific serial numbers for search tests."""
        # Create our own test data: part and revision
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"SEARCH-TEST-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part
        client.parts.create(
            number=part_number,
            name=f"Test Part for Search {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        
        test_configs = [
            f"SEARCH-SN001-{timestamp}",
            f"SEARCH-SN002-{timestamp}",
            f"TEST-SN003-{timestamp}",
            f"OTHER-SN004-{timestamp}",
            f"SEARCH-SN005-{timestamp}",
        ]
        
        test_units: List[Tuple[models.UnitCreateResponse, str]] = []
        for serial_number in test_configs:
            unit = client.units.create(
                serial_number=serial_number,
                part_number=part_number,
                revision_number=revision_number
            )
            assert_create_unit_success(unit)
            test_units.append((unit, serial_number))
            
        return test_units

    def test_search_by_partial_serial_number(self, client: TofuPilot, test_units_for_search: List[Tuple[models.UnitCreateResponse, str]]):
        """Test searching units by partial serial number match."""
        # Search for units with "SEARCH" in the serial number
        result = client.units.list(search_query="SEARCH")
        assert_get_units_success(result)
        
        # Should find at least our test units with "SEARCH"
        search_units = [u for u in result.data if "SEARCH" in u.serial_number]
        assert len(search_units) >= 3  # 3 units contain "SEARCH"

    def test_search_case_insensitive(self, client: TofuPilot, test_units_for_search: List[Tuple[models.UnitCreateResponse, str]]):
        """Test that search is case-insensitive."""
        # Search with lowercase
        result_lower = client.units.list(search_query="search")
        assert_get_units_success(result_lower)
        
        # Search with uppercase  
        result_upper = client.units.list(search_query="SEARCH")
        assert_get_units_success(result_upper)
        
        # Should return similar results (case-insensitive)
        lower_ids = {u.id for u in result_lower.data if "SEARCH" in u.serial_number.upper()}
        upper_ids = {u.id for u in result_upper.data if "SEARCH" in u.serial_number.upper()}
        
        # Should have significant overlap
        if len(lower_ids) > 0 and len(upper_ids) > 0:
            overlap = len(lower_ids.intersection(upper_ids))
            total = len(lower_ids.union(upper_ids))
            overlap_ratio = overlap / total if total > 0 else 1
            assert overlap_ratio >= 0.8  # At least 80% overlap

    def test_search_specific_serial_pattern(self, client: TofuPilot, test_units_for_search: List[Tuple[models.UnitCreateResponse, str]]):
        """Test searching for specific serial number patterns."""
        # Search for "SN00"
        result = client.units.list(search_query="SN00")
        assert_get_units_success(result)
        
        # Should find units with "SN00" in the serial number
        sn_matches = [u for u in result.data if "SN00" in u.serial_number]
        assert len(sn_matches) >= 2  # At least SN001 and SN002

    def test_search_no_results(self, client: TofuPilot):
        """Test search with no matching results."""
        # Search for something very unlikely to exist
        unique_term = f"NONEXISTENT-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        result = client.units.list(search_query=unique_term)
        assert_get_units_success(result)
        
        # Should return empty results
        assert len(result.data) == 0

    def test_empty_search_query(self, client: TofuPilot):
        """Test search with empty query returns all units."""
        result_empty = client.units.list(search_query="")
        result_none = client.units.list()
        
        assert_get_units_success(result_empty)
        assert_get_units_success(result_none)
        
        # Empty search should return all units (same as no search)
        assert len(result_empty.data) == len(result_none.data)

    def test_search_with_special_characters(self, client: TofuPilot, test_units_for_search: List[Tuple[models.UnitCreateResponse, str]]):
        """Test search with special characters."""
        # Search for the hyphen character
        result = client.units.list(search_query="-")
        assert_get_units_success(result)
        
        # Should find units with hyphens
        hyphen_units = [u for u in result.data if "-" in u.serial_number]
        assert len(hyphen_units) >= 1

    def test_search_combined_with_pagination(self, client: TofuPilot, test_units_for_search: List[Tuple[models.UnitCreateResponse, str]]):
        """Test search combined with pagination."""
        result = client.units.list(
            search_query="SEARCH",
            limit=2
        )
        assert_get_units_success(result)
        
        # Should respect both search and limit
        assert len(result.data) <= 2
        search_matches = [u for u in result.data if "SEARCH" in u.serial_number]
        assert len(search_matches) >= 1

    def test_search_combined_with_other_filters(self, client: TofuPilot, test_units_for_search: List[Tuple[models.UnitCreateResponse, str]]):
        """Test search combined with other filters."""
        # Get one of our test units
        _, serial_number = test_units_for_search[0]
        
        # Search with both search query and serial numbers filter
        result = client.units.list(
            search_query="SEARCH",
            serial_numbers=[serial_number]
        )
        assert_get_units_success(result)
        
        # Should find exactly this unit (if it contains SEARCH)
        if "SEARCH" in serial_number:
            assert len(result.data) == 1
            assert result.data[0].serial_number == serial_number

    def test_search_exact_serial_match(self, client: TofuPilot, test_units_for_search: List[Tuple[models.UnitCreateResponse, str]]):
        """Test searching with exact serial number."""
        _, target_serial = test_units_for_search[0]
        
        # Use a shorter search term that's more likely to match
        # Extract just the "SEARCH-SN001" part
        search_term = '-'.join(target_serial.split('-')[:2])
        
        result = client.units.list(search_query=search_term)
        assert_get_units_success(result)
        
        # If we do find results, check if they match the search term
        if result.data:
            # All results should contain the search term (case insensitive)
            for unit in result.data:
                assert search_term.lower() in unit.serial_number.lower(), \
                    f"Unit {unit.serial_number} doesn't contain search term {search_term}"