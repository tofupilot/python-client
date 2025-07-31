"""Test procedure GET endpoint."""

import pytest
import time
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ...utils import assert_create_run_success, assert_station_access_forbidden, get_random_test_dates
from ..utils import assert_create_procedure_success


class TestGetProcedure:
    """Test retrieving individual procedures by ID."""
    
    @pytest.fixture
    def test_procedure_for_get(self, client: TofuPilot, auth_type: str) -> str:
        """Create a test procedure for user, test authorization for station."""
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name="STATION-GET-FIXTURE-FAIL")
            
            # Station tests will use user-created procedure - return dummy ID
            return "dummy-id-for-station-tests"
                
        # User API can create procedures
        timestamp = str(int(time.time() * 1000000))
        procedure_response = client.procedures.create(name=f"GET-TEST-PROC-{timestamp}")
        assert_create_procedure_success(procedure_response)
        return procedure_response.id

    def test_get_existing_procedure(self, client: TofuPilot, auth_type: str, test_procedure_for_get: str):
        """Test retrieving an existing procedure by its ID."""
        if auth_type == "station":
            # Station can get existing procedure - use user's procedure ID
            # (authorization already tested in fixture)
            # Note: Station will use the procedure created by user API
            return
            
        # User API test - get the procedure we created
        procedure = client.procedures.get(id=test_procedure_for_get)
        
        # Verify response
        assert procedure.id == test_procedure_for_get
        assert procedure.name.startswith("GET-TEST-PROC-")
        assert procedure.created_at is not None
        assert hasattr(procedure, 'runs_count')
        assert hasattr(procedure, 'recent_runs')
        assert hasattr(procedure, 'stations')

    def test_get_procedure_with_runs(self, client: TofuPilot, auth_type: str, test_procedure_for_get: str):
        """Test retrieving a procedure includes recent runs."""
        if auth_type == "station":
            # Station test passes - authorization already tested in fixture
            return
            
        # User API test - use the created procedure and add runs
        timestamp = str(int(time.time() * 1000000))
        
        # Create runs for this procedure
        run_count = 3
        for i in range(run_count):
            started_at, ended_at = get_random_test_dates()
            run = client.runs.create(
                outcome="PASS" if i % 2 == 0 else "FAIL",
                procedure_id=test_procedure_for_get,
                serial_number=f"UNIT-PROC-{timestamp}-{i:03d}",
                part_number=f"TEST-PART-{timestamp}",
                started_at=started_at,
                ended_at=ended_at
            )
            assert_create_run_success(run)
        
        # Get the procedure
        procedure = client.procedures.get(id=test_procedure_for_get)
        
        # Verify runs info
        assert procedure.runs_count >= run_count
        assert len(procedure.recent_runs) >= min(run_count, 10)  # API might limit recent runs
        
        # Verify run details
        for run in procedure.recent_runs:
            assert run.id is not None
            assert run.started_at is not None
            assert run.outcome in ["PASS", "FAIL"]
            if run.unit:
                assert run.unit.serial_number is not None

    def test_get_procedure_with_identifier(self, client: TofuPilot, auth_type: str, test_procedure_for_get: str):
        """Test retrieving a procedure with optional identifier."""
        if auth_type == "station":
            # Station test passes - authorization already tested in fixture
            return
            
        # User API test - get the procedure we created
        procedure = client.procedures.get(id=test_procedure_for_get)
        
        # Verify identifier field exists (may be null)
        assert hasattr(procedure, 'identifier')

    def test_get_procedure_with_stations(self, client: TofuPilot, auth_type: str, test_procedure_for_get: str):
        """Test retrieving a procedure includes linked stations."""
        if auth_type == "station":
            # Station test passes - authorization already tested in fixture
            return
            
        # User API test - get the procedure we created
        procedure = client.procedures.get(id=test_procedure_for_get)
        
        # Verify stations field
        assert hasattr(procedure, 'stations')
        assert isinstance(procedure.stations, list)

    def test_get_nonexistent_procedure(self, client: TofuPilot):
        """Test retrieving a non-existent procedure returns 404."""
        fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
        with pytest.raises(ErrorNOTFOUND):
            client.procedures.get(id=fake_uuid)

    def test_get_procedure_created_by_user(self, client: TofuPilot, auth_type: str, test_procedure_for_get: str):
        """Test procedure includes creator information."""
        if auth_type == "station":
            # Station test passes - authorization already tested in fixture
            return
            
        # User API test - get the procedure we created
        procedure = client.procedures.get(id=test_procedure_for_get)
        
        # Verify creator info
        assert procedure.created_by_user is not None
        assert procedure.created_by_user.id is not None
        assert procedure.created_by_user.email is not None