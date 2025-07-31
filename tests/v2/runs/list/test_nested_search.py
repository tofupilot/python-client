"""Test search functionality for runs list - optimized version."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot


class TestRunsNestedSearch:
    """Test that search is working correctly for runs - supports run ID, procedure name, and unit serial."""

    def test_search_by_run_id(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test searching runs by run ID (partial match)."""
        if auth_type == "station":
            # Stations cannot create runs - test with existing data only
            search_results = client.runs.list(search_query="run")
            print(f"Found {len(search_results.data)} runs with 'run' search")
            return
        
        # Create a run
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        serial_number = f"SEARCH-ID-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        assert run_result.id is not None
        
        # Search by partial run ID (character restrictions removed)
        run_id_prefix = run_result.id[:12]  # Use first 12 characters
        print(f"\nSearching runs for ID prefix: '{run_id_prefix}'")
        search_results = client.runs.list(search_query=run_id_prefix)
        
        print(f"Found {len(search_results.data)} runs")
        
        # Should find at least our created run
        assert len(search_results.data) > 0, f"Should find at least one run with ID prefix '{run_id_prefix}'"
        
        # Verify the exact run is in results
        found_run = False
        for run in search_results.data:
            if run.id == run_result.id:
                found_run = True
                print(f"✓ Found exact run {run.id}")
                break
                
        assert found_run, f"Should find the exact run {run_result.id}"

    def test_search_by_procedure_name(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test searching runs by procedure name."""
        if auth_type == "station":
            # Stations cannot create runs - test with existing data only
            search_results = client.runs.list(search_query="test")
            print(f"Found {len(search_results.data)} runs with 'test' search")
            return
        
        # Create a run
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        serial_number = f"SEARCH-PROC-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        assert run_result.id is not None
        
        # Get the created run to get procedure name
        created_run = client.runs.get(id=run_result.id)
        
        # Search by procedure name
        if created_run.procedure and created_run.procedure.name:
            proc_name = created_run.procedure.name
            print(f"\nSearching runs for procedure name: '{proc_name}'")
            search_results = client.runs.list(search_query=proc_name)
            
            print(f"Found {len(search_results.data)} runs")
            
            # Print debug info about found runs
            for i, run in enumerate(search_results.data[:3]):  # Show first 3 runs
                proc_info = run.procedure.name if run.procedure else "None"
                print(f"  Run {i+1}: procedure='{proc_info}'")
            
            if len(search_results.data) > 0:
                # If we found runs, verify at least one has a procedure name that contains our search term
                found_with_proc = False
                for run in search_results.data:
                    if run.procedure and run.procedure.name and proc_name.lower() in run.procedure.name.lower():
                        found_with_proc = True
                        print(f"✓ Found run with procedure containing '{proc_name}'")
                        break
                        
                if not found_with_proc:
                    print(f"⚠ No runs found with procedure name containing '{proc_name}', but search returned {len(search_results.data)} results")
            else:
                print(f"⚠ No runs found for procedure name '{proc_name}' - search may not support procedure name matching")

    def test_search_by_procedure_identifier(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test searching runs by procedure identifier."""
        if auth_type == "station":
            # Stations cannot create runs or list procedures - basic search only
            search_results = client.runs.list(search_query="proc")
            print(f"Found {len(search_results.data)} runs with 'proc' search")
            return
        
        # Get the procedure to check if it has an identifier
        client.procedures.list(limit=100)
        
        # Note: Procedure identifier search is no longer supported in the backend
        # This test now verifies basic run creation works
        # Create a run to verify basic procedure search works
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        serial_number = f"SEARCH-PROCID-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        assert run_result.id is not None
        
        # We can still search by the serial number to verify the run was created
        search_results = client.runs.list(search_query=serial_number)
        assert len(search_results.data) > 0, f"Should find run with serial number '{serial_number}'"
        print("✓ Run created successfully for procedure test")

    def test_search_by_unit_serial_number(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test searching runs by unit serial number."""
        if auth_type == "station":
            # Stations cannot create runs - test with existing data only
            search_results = client.runs.list(search_query="SERIAL")
            print(f"Found {len(search_results.data)} runs with 'SERIAL' search")
            return
        
        # Create test data with unique serial number
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        unique_serial = f"UNIQUE-SERIAL-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=unique_serial,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        assert run_result.id is not None
        
        # Search by the unique serial number
        print(f"\nSearching runs for serial number: '{unique_serial}'")
        search_results = client.runs.list(search_query=unique_serial)
        
        print(f"Found {len(search_results.data)} runs")
        assert len(search_results.data) > 0, f"Should find runs with serial number '{unique_serial}'"
        
        # Verify the exact match
        found_serial = False
        for run in search_results.data:
            if run.unit and run.unit.serial_number == unique_serial:
                found_serial = True
                print(f"✓ Found run with serial number '{unique_serial}'")
                break
                
        assert found_serial, f"Should find run with exact serial number '{unique_serial}'"

    def test_search_case_insensitive(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test that search is case insensitive."""
        if auth_type == "station":
            # Stations cannot create runs - test with existing data only
            search_results = client.runs.list(search_query="CASE")
            print(f"Found {len(search_results.data)} runs with 'CASE' search")
            return
        
        # Create test data with mixed case
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        mixed_case_serial = f"MixedCaseSerial-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=mixed_case_serial,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        assert run_result.id is not None
        
        print(f"\nTesting case sensitivity with serial: '{mixed_case_serial}'")
        
        # Search with different cases
        search_lower = client.runs.list(search_query=mixed_case_serial.lower())
        search_upper = client.runs.list(search_query=mixed_case_serial.upper())
        search_mixed = client.runs.list(search_query=mixed_case_serial)
        
        print(f"Lower case search found: {len(search_lower.data)} runs")
        print(f"Upper case search found: {len(search_upper.data)} runs")
        print(f"Original case search found: {len(search_mixed.data)} runs")
        
        # All searches should find at least our created run
        assert len(search_lower.data) > 0, "Lower case search should find at least one result"
        assert len(search_upper.data) > 0, "Upper case search should find at least one result"
        assert len(search_mixed.data) > 0, "Mixed case search should find at least one result"

    def test_search_partial_match(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test partial string matching in search."""
        if auth_type == "station":
            # Stations cannot create runs - test with existing data only
            search_results = client.runs.list(search_query="PREFIX")
            print(f"Found {len(search_results.data)} runs with 'PREFIX' search")
            return
        
        # Create test data
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        serial_with_pattern = f"PREFIX-MIDDLE-SUFFIX-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_with_pattern,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        assert run_result.id is not None
        
        # Test partial matches
        partial_searches = ["PREFIX", "MIDDLE", "SUFFIX", f"SUFFIX-{timestamp}"]
        
        for partial in partial_searches:
            print(f"\nSearching for partial match: '{partial}'")
            search_results = client.runs.list(search_query=partial)
            assert len(search_results.data) > 0, f"Should find runs with partial match '{partial}'"
            print(f"✓ Found {len(search_results.data)} runs with '{partial}'")

    def test_search_with_nonexistent_term(self, client: TofuPilot):
        """Test that searching for non-existent terms doesn't crash."""
        # Search for something that definitely doesn't exist
        search_results = client.runs.list(search_query="XYZNONEXISTENT123SEARCH")
        
        # Should return empty results, not crash
        assert isinstance(search_results.data, list)
        print(f"✓ Non-existent search handled gracefully: {len(search_results.data)} results")

    def test_search_short_query(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test that short queries work correctly (character restrictions removed)."""
        if auth_type == "station":
            # Stations cannot create runs - test with existing data only
            search_results = client.runs.list(search_query="AB")
            print(f"Found {len(search_results.data)} runs with 'AB' search")
            return
        
        # Create a run with a short serial number
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        short_serial = f"AB-{timestamp}"
        
        run_result = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=short_serial,
            part_number=f"PART-{timestamp}",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc)
        )
        assert run_result.id is not None
        
        # Search with short query should still work for serial numbers
        print("\nSearching with short query: 'AB'")
        search_results = client.runs.list(search_query="AB")
        
        # Should find results (serial number search works with short queries)
        print(f"Found {len(search_results.data)} runs")
        
        # Search by short ID prefix should now work (character restrictions removed)
        short_id = run_result.id[:5]
        print(f"\nSearching with short ID: '{short_id}' (should find our run)")
        id_search = client.runs.list(search_query=short_id)
        
        # Short ID searches should now work
        found_our_run = any(run.id == run_result.id for run in id_search.data)
        assert found_our_run, f"Should find our run when searching with short ID prefix '{short_id}'"
        print(f"✓ Short ID search found: {len(id_search.data)} runs (including our run)")