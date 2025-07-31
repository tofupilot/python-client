"""Test that character restrictions have been removed from units search."""

import pytest
from tofupilot.v2 import TofuPilot
from datetime import datetime, timezone


class TestUnitsNoCharacterRestrictions:
    """Verify that units search works without character restrictions."""

    def test_short_search_queries_work(self, client: TofuPilot):
        """Test that 1-2 character searches work (previously restricted to 3+)."""
        # Test 1-character search
        response = client.units.list(search_query="A", limit=100)
        assert isinstance(response.data, list), "1-character search should work"
        print("✓ 1-character search works")
        
        # Test 2-character search
        response = client.units.list(search_query="AB", limit=100)
        assert isinstance(response.data, list), "2-character search should work"
        print("✓ 2-character search works")

    def test_short_search_with_created_unit(self, client: TofuPilot):
        """Test short searches work with created test data."""
        # Create test data
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"PART-{timestamp}"
        
        # Create part and revision
        client.parts.create(
            number=part_number,
            name=f"Test Part {timestamp}"
        )
        
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=f"REV-{timestamp}"
        )
        
        # Create unit with short searchable patterns
        serial_number = f"AB-SHORT-{timestamp}"
        unit_result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=f"REV-{timestamp}"
        )
        
        # Test 1-character search
        response = client.units.list(search_query="A", limit=100)
        assert isinstance(response.data, list), "1-character search should work"
        found_serials = [unit.serial_number for unit in response.data]
        assert serial_number in found_serials, "Should find unit with 1-character search"
        print("✓ 1-character search finds our unit")
        
        # Test 2-character search
        response = client.units.list(search_query="AB", limit=100)
        assert isinstance(response.data, list), "2-character search should work"
        found_serials = [unit.serial_number for unit in response.data]
        assert serial_number in found_serials, "Should find unit with 2-character search"
        print("✓ 2-character search finds our unit")

    def test_substring_matching_everywhere(self, client: TofuPilot):
        """Test that substring matching works (not just prefix matching)."""
        # Create test data
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"PART-{timestamp}"
        
        # Create part and revision
        client.parts.create(
            number=part_number,
            name=f"Test Part {timestamp}"
        )
        
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=f"REV-{timestamp}"
        )
        
        # Create unit with substring patterns
        serial_number = f"PREFIX-MIDDLE-SUFFIX-{timestamp}"
        unit_result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=f"REV-{timestamp}"
        )
        
        # Test searching for middle substring
        response = client.units.list(search_query="MIDDLE", limit=100)
        assert isinstance(response.data, list), "Substring search should work"
        found_serials = [unit.serial_number for unit in response.data]
        assert serial_number in found_serials, "Should find unit by middle substring"
        print("✓ Middle substring search works")
        
        # Test searching for suffix substring
        response = client.units.list(search_query="SUFFIX", limit=100)
        assert isinstance(response.data, list), "Suffix search should work"
        found_serials = [unit.serial_number for unit in response.data]
        assert serial_number in found_serials, "Should find unit by suffix substring"
        print("✓ Suffix substring search works")

    def test_empty_and_single_char_edge_cases(self, client: TofuPilot):
        """Test edge cases with empty and single character searches."""
        # Empty search should return results
        response = client.units.list(search_query="", limit=5)
        assert isinstance(response.data, list), "Empty search should work"
        print("✓ Empty search returns results")
        
        # Single special characters should work
        for char in ["@", "-", "_", "."]:
            response = client.units.list(search_query=char, limit=5)
            assert isinstance(response.data, list), f"Single character '{char}' search should work"
        print("✓ Single special character searches work")

    def test_search_across_multiple_fields(self, client: TofuPilot):
        """Test that search works across serial number, part name, part number, and revision."""
        # Create test data with searchable patterns in different fields
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"SEARCHABLE-PART-{timestamp}"
        part_name = f"Searchable Test Part {timestamp}"
        revision_number = f"SEARCHABLE-REV-{timestamp}"
        
        # Create part and revision
        client.parts.create(
            number=part_number,
            name=part_name
        )
        
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create unit
        serial_number = f"UNIT-{timestamp}"
        unit_result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number
        )
        
        # Test search by part number
        response = client.units.list(search_query="SEARCHABLE-PART", limit=100)
        assert isinstance(response.data, list), "Part number search should work"
        found_ids = [unit.id for unit in response.data]
        assert unit_result.id in found_ids, "Should find unit by part number"
        print("✓ Part number search works")
        
        # Test search by part name  
        response = client.units.list(search_query="Searchable Test", limit=100)
        assert isinstance(response.data, list), "Part name search should work"
        found_ids = [unit.id for unit in response.data]
        assert unit_result.id in found_ids, "Should find unit by part name"
        print("✓ Part name search works")
        
        # Test search by revision number
        response = client.units.list(search_query="SEARCHABLE-REV", limit=100)
        assert isinstance(response.data, list), "Revision number search should work"
        found_ids = [unit.id for unit in response.data]
        assert unit_result.id in found_ids, "Should find unit by revision number"
        print("✓ Revision number search works")

    def test_short_searches_in_all_fields(self, client: TofuPilot):
        """Test that short searches work across all searchable fields."""
        # Create test data with 2-character patterns in different fields
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"XY-PART-{timestamp}"
        part_name = f"XY Test Part {timestamp}"
        revision_number = f"XY-REV-{timestamp}"
        
        # Create part and revision
        client.parts.create(
            number=part_number,
            name=part_name
        )
        
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create unit
        serial_number = f"XY-UNIT-{timestamp}"
        unit_result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number
        )
        
        # Test 2-character search should find the unit via any of the fields
        response = client.units.list(search_query="XY", limit=100)
        assert isinstance(response.data, list), "2-character cross-field search should work"
        found_ids = [unit.id for unit in response.data]
        assert unit_result.id in found_ids, "Should find unit with 2-character search across fields"
        print("✓ 2-character cross-field search works")