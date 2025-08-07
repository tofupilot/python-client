"""Test that character restrictions have been removed from procedures search."""

import pytest
from tofupilot.v2 import TofuPilot
from datetime import datetime, timezone
from ...utils import assert_station_access_forbidden


class TestProceduresNoCharacterRestrictions:
    """Verify that procedures search works without character restrictions."""

    def test_short_search_queries_work(self, client: TofuPilot, auth_type: str):
        """Test that 1-2 character searches work (previously restricted to 3+)."""
        # Test 1-character search
        response = client.procedures.list(search_query="a", limit=100)
        assert isinstance(response.data, list), "1-character search should work"
        print("✓ 1-character search works")
        
        # Test 2-character search
        response = client.procedures.list(search_query="te", limit=100)
        assert isinstance(response.data, list), "2-character search should work"
        print("✓ 2-character search works")

    def test_short_procedure_id_search(self, client: TofuPilot, auth_type: str, timestamp: str):
        """Test that procedure ID search works with less than 6 characters (previously restricted)."""
        if auth_type == "station":
            # Stations cannot create procedures, but can still search
            # Use existing procedures for search testing
            procedures_response = client.procedures.list(limit=10)
            if not procedures_response.data:
                # If no procedures exist, we can't test ID search
                return
            test_procedure = procedures_response.data[0]
        else:
            # Create a procedure to test with
            procedure_response = client.procedures.create(
                name=f"Test Procedure for ID Search {timestamp}"
            )
            # Need to get the full procedure to access all fields
            test_procedure = client.procedures.get(id=procedure_response.id)
        
        # Search with first 3 characters of procedure ID
        short_id_search = test_procedure.id[:3]
        response = client.procedures.list(search_query=short_id_search, limit=100)
        assert isinstance(response.data, list), f"3-character ID search should work"
        found_ids = [proc.id for proc in response.data]
        assert test_procedure.id in found_ids, f"Should find procedure with 3-character ID prefix: {short_id_search}"
        print(f"✓ 3-character ID search works (searched for '{short_id_search}')")
        
        # Search with first 5 characters of procedure ID
        medium_id_search = test_procedure.id[:5]
        response = client.procedures.list(search_query=medium_id_search, limit=100)
        assert isinstance(response.data, list), f"5-character ID search should work"
        found_ids = [proc.id for proc in response.data]
        assert test_procedure.id in found_ids, f"Should find procedure with 5-character ID prefix: {medium_id_search}"
        print(f"✓ 5-character ID search works (searched for '{medium_id_search}')")

    def test_substring_matching_everywhere(self, client: TofuPilot, auth_type: str, timestamp: str):
        """Test that substring matching works (not just prefix matching)."""
        if auth_type == "station":
            # Stations cannot create procedures, but can test search functionality
            # with existing procedures. Test general substring search behavior.
            response = client.procedures.list(search_query="test", limit=100)
            assert isinstance(response.data, list), "Substring search should work for stations"
            
            # Test short substring search
            response = client.procedures.list(search_query="te", limit=100)
            assert isinstance(response.data, list), "Short substring search should work for stations"
            print("✓ Station substring search works")
            return
        
        # For users, create procedures with specific multi-word names for testing
        
        # Create a procedure with a multi-word name
        procedure_name = f"Automated Battery Testing Procedure {timestamp}"
        created_procedure = client.procedures.create(name=procedure_name)
        
        # Also create some other procedures to ensure we're testing search filtering
        client.procedures.create(name=f"Simple Test {timestamp}")
        client.procedures.create(name=f"Another Procedure {timestamp}")
        
        # We know the name we created, so use it directly
        middle_word = "Battery"  # We know this is in the middle
        
        # Test searching for middle substring
        response = client.procedures.list(search_query=middle_word, limit=100)
        assert isinstance(response.data, list), "Substring search should work"
        found_ids = [proc.id for proc in response.data]
        assert created_procedure.id in found_ids, f"Should find procedure by middle substring '{middle_word}'"
        print(f"✓ Middle substring search works (searched for '{middle_word}')")
        
        # Test with another middle word
        another_middle_word = "Testing"
        response = client.procedures.list(search_query=another_middle_word, limit=100)
        assert isinstance(response.data, list), "Substring search should work"
        found_ids = [proc.id for proc in response.data]
        assert created_procedure.id in found_ids, f"Should find procedure by middle substring '{another_middle_word}'"
        print(f"✓ Another middle substring search works (searched for '{another_middle_word}')")

    def test_empty_and_single_char_edge_cases(self, client: TofuPilot, auth_type: str):
        """Test edge cases with empty and single character searches."""
        # Empty search should return results
        response = client.procedures.list(search_query="", limit=5)
        assert isinstance(response.data, list), "Empty search should work"
        print("✓ Empty search returns results")
        
        # Single special characters should work
        for char in ["@", "-", "_", "."]:
            response = client.procedures.list(search_query=char, limit=5)
            assert isinstance(response.data, list), f"Single character '{char}' search should work"
        print("✓ Single special character searches work")

    def test_procedure_name_search_consistency(self, client: TofuPilot, auth_type: str, timestamp: str):
        """Test that procedure name search is consistent with substring matching."""
        if auth_type == "station":
            # Stations can test search but not create procedures
            # Test partial name searches work in general
            for search_term in ["test", "te", "t"]:
                response = client.procedures.list(search_query=search_term, limit=100)
                assert isinstance(response.data, list), f"Search for '{search_term}' should work"
                print(f"✓ Search for '{search_term}' works")
            return
            
        # For users, create a procedure with a known name containing "test"
        procedure_name = f"Test Procedure Consistency Check {timestamp}"
        test_procedure = client.procedures.create(name=procedure_name)
        
        # Test partial name searches
        for search_term in ["test", "te", "t"]:
            response = client.procedures.list(search_query=search_term, limit=100)
            assert isinstance(response.data, list), f"Search for '{search_term}' should work"
            print(f"✓ Search for '{search_term}' works")
        
        # Verify our specific procedure can be found with partial search
        response = client.procedures.list(search_query="Consistency", limit=100)
        found_ids = [proc.id for proc in response.data]
        assert test_procedure.id in found_ids, "Should find procedure by partial name match"