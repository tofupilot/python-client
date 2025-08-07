"""Test that character restrictions have been removed from runs search."""

import pytest
from tofupilot.v2 import TofuPilot
from datetime import datetime, timezone


class TestRunsNoCharacterRestrictions:
    """Verify that runs search works without character restrictions."""

    def test_short_search_queries_work(self, client: TofuPilot, procedure_id: str, timestamp: str):
        """Test that 1-2 character searches work (previously restricted to 3+)."""
        # Create a test run with a searchable serial number
        serial_number = f"AB-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        
        # Test 1-character search
        response = client.runs.list(search_query="A", limit=100)
        assert isinstance(response.data, list), "1-character search should work"
        found_ids = [run.id for run in response.data]
        assert run_result.id in found_ids, "Should find run with 1-character search"
        print("✓ 1-character search works")
        
        # Test 2-character search
        response = client.runs.list(search_query="AB", limit=100)
        assert isinstance(response.data, list), "2-character search should work"
        found_ids = [run.id for run in response.data]
        assert run_result.id in found_ids, "Should find run with 2-character search"
        print("✓ 2-character search works")

    def test_short_run_id_search(self, client: TofuPilot, procedure_id: str, timestamp: str):
        """Test that run ID search works with less than 6 characters (previously restricted)."""
        # Create a test run
        serial_number = f"ID-TEST-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        
        # Search with first 3 characters of run ID
        short_id_search = run_result.id[:3]
        response = client.runs.list(search_query=short_id_search, limit=100)
        assert isinstance(response.data, list), f"3-character ID search should work"
        found_ids = [run.id for run in response.data]
        assert run_result.id in found_ids, f"Should find run with 3-character ID prefix: {short_id_search}"
        print(f"✓ 3-character ID search works (searched for '{short_id_search}')")
        
        # Search with first 5 characters of run ID
        medium_id_search = run_result.id[:5]
        response = client.runs.list(search_query=medium_id_search, limit=100)
        assert isinstance(response.data, list), f"5-character ID search should work"
        found_ids = [run.id for run in response.data]
        assert run_result.id in found_ids, f"Should find run with 5-character ID prefix: {medium_id_search}"
        print(f"✓ 5-character ID search works (searched for '{medium_id_search}')")

    def test_substring_matching_everywhere(self, client: TofuPilot, procedure_id: str, timestamp: str):
        """Test that substring matching works (not just prefix matching)."""
        # Create a test run with a specific serial number pattern
        serial_number = f"PREFIX-MIDDLE-SUFFIX-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        
        # Test searching for middle substring
        response = client.runs.list(search_query="MIDDLE", limit=100)
        assert isinstance(response.data, list), "Substring search should work"
        found_ids = [run.id for run in response.data]
        assert run_result.id in found_ids, "Should find run by middle substring"
        print("✓ Middle substring search works")
        
        # Test searching for suffix substring
        response = client.runs.list(search_query="SUFFIX", limit=100)
        assert isinstance(response.data, list), "Suffix search should work"
        found_ids = [run.id for run in response.data]
        assert run_result.id in found_ids, "Should find run by suffix substring"
        print("✓ Suffix substring search works")

    def test_empty_and_single_char_edge_cases(self, client: TofuPilot):
        """Test edge cases with empty and single character searches."""
        # Empty search should return results
        response = client.runs.list(search_query="", limit=5)
        assert isinstance(response.data, list), "Empty search should work"
        print("✓ Empty search returns results")
        
        # Single special characters should work
        for char in ["@", "-", "_", "."]:
            response = client.runs.list(search_query=char, limit=5)
            assert isinstance(response.data, list), f"Single character '{char}' search should work"
        print("✓ Single special character searches work")