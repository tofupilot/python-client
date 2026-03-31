"""Validate that runs search functionality works correctly - optimized version."""

from tofupilot.v2 import TofuPilot


class TestRunsSearchValidation:
    """Validate runs search functionality for supported fields only."""

    def test_search_returns_results_without_error(self, client: TofuPilot):
        """Test that all search scenarios work without crashing."""
        
        # Test 1: Basic search should work
        response = client.runs.list(search_query="test", limit=5)
        assert isinstance(response.data, list), "Search should return a list"
        print(f"✓ Basic search works: found {len(response.data)} runs")
        
        # Test 2: Empty search should work
        response = client.runs.list(search_query="", limit=5)
        assert isinstance(response.data, list), "Empty search should work"
        print(f"✓ Empty search works: found {len(response.data)} runs")
        
        # Test 3: Non-existent search should work (return empty)
        response = client.runs.list(search_query="DEFINITELY_NONEXISTENT_SEARCH_TERM_XYZ123", limit=5)
        assert isinstance(response.data, list), "Non-existent search should return empty list"
        print(f"✓ Non-existent search works: found {len(response.data)} runs")
        
        # Test 4: Special characters should work
        response = client.runs.list(search_query="test-123_special@chars", limit=5)
        assert isinstance(response.data, list), "Special characters search should work"
        print(f"✓ Special characters search works: found {len(response.data)} runs")
        
        # Test 5: Case variations should work
        for search_term in ["TEST", "test", "TeSt"]:
            response = client.runs.list(search_query=search_term, limit=5)
            assert isinstance(response.data, list), f"Case variation '{search_term}' should work"
        print("✓ Case variations work")

    def test_search_with_existing_data(self, client: TofuPilot, procedure_id: str, timestamp: str):
        """Test search against test data we create - only supported fields."""
        from datetime import datetime, timezone
        
        # Create test run with searchable serial number
        serial_number = f"SEARCHABLE-UNIT-{timestamp}"
        
        # Create run
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        
        # Test search by serial number (supported)
        response = client.runs.list(search_query=serial_number)
        found_run_ids = [run.id for run in response.data]
        assert run_result.id in found_run_ids, f"Should find run {run_result.id} when searching by serial number"
        print("✓ Found run by serial number search")
        
        # Test search by partial serial number
        partial_search = "SEARCHABLE"
        response = client.runs.list(search_query=partial_search)
        found_run_ids = [run.id for run in response.data]
        assert run_result.id in found_run_ids, f"Should find run {run_result.id} when searching by partial serial"
        print("✓ Found run by partial serial number search")
        
        # Test search by run ID (must be at least 8 characters)
        if len(run_result.id) >= 8:
            id_prefix = run_result.id[:12]
            response = client.runs.list(search_query=id_prefix)
            found_run_ids = [run.id for run in response.data]
            assert run_result.id in found_run_ids, "Should find run by ID prefix"
            print("✓ Found run by ID prefix search")

    def test_nested_fields_accessible(self, client: TofuPilot, procedure_id: str, timestamp: str):
        """Test that result objects have correct nested structure."""
        # Create a simple run
        from datetime import datetime, timezone
        
        serial_number = f"NESTED-TEST-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        
        # Search and verify structure
        response = client.runs.list(search_query=serial_number, limit=10)
        
        # Find our run in results
        our_run = None
        for run in response.data:
            if run.id == run_result.id:
                our_run = run
                break
        
        assert our_run is not None, "Should find our created run"
        
        # Verify nested fields exist
        assert hasattr(our_run, 'id'), "Run should have id"
        assert hasattr(our_run, 'outcome'), "Run should have outcome"
        
        # Check procedure info
        if our_run.procedure:
            assert hasattr(our_run.procedure, 'id'), "Procedure should have id"
            assert hasattr(our_run.procedure, 'name'), "Procedure should have name"
            print("✓ Procedure nested fields accessible")
        
        # Check unit info
        if our_run.unit:
            assert hasattr(our_run.unit, 'id'), "Unit should have id"
            assert hasattr(our_run.unit, 'serial_number'), "Unit should have serial_number"
            print("✓ Unit nested fields accessible")
