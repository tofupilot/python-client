"""Test user and station filtering parameters in runs.list()."""

import pytest
from datetime import datetime, timezone
from typing import Dict, Any
from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success, assert_get_runs_success


class TestRunsUserStationFiltering:
    """Test user and station filtering parameters."""
    
    @pytest.fixture
    def user_client(self, user_api_key: str, tofupilot_server_url: str) -> TofuPilot:
        """Create a client with user API key."""
        return TofuPilot(
            api_key=user_api_key,
            server_url=f"{tofupilot_server_url}/api",
        )
    
    @pytest.fixture
    def station_client(self, station_api_key: str, tofupilot_server_url: str) -> TofuPilot:
        """Create a client with station API key."""
        return TofuPilot(
            api_key=station_api_key,
            server_url=f"{tofupilot_server_url}/api",
        )
    
    @pytest.fixture 
    def test_runs_with_auth_info(self, user_client: TofuPilot, station_client: TofuPilot, procedure_id: str) -> Dict[str, Any]:
        """Create test runs with different authentication and extract created_by IDs."""
        base_time = datetime.now(timezone.utc)
        created_data: Dict[str, Any] = {
            "user_runs": [],
            "station_runs": [],
            "user_id": None,
            "station_id": None,
        }
        
        # Create runs with user API key
        for i in range(2):
            run = user_client.runs.create(
                outcome="PASS" if i == 0 else "FAIL",
                procedure_id=procedure_id,
                serial_number=f"USER-AUTH-TEST-{i}",
                part_number="PCB-001",
                started_at=base_time,
                ended_at=base_time
            )
            assert_create_run_success(run)
            created_data["user_runs"].append(run)
        
        # Create runs with station API key
        for i in range(2):
            run = station_client.runs.create(
                outcome="PASS" if i == 0 else "FAIL",
                procedure_id=procedure_id,
                serial_number=f"STATION-AUTH-TEST-{i}",
                part_number="PCB-001",
                started_at=base_time,
                ended_at=base_time
            )
            assert_create_run_success(run)
            created_data["station_runs"].append(run)
        
        # Get the created_by IDs from the created runs
        if created_data["user_runs"]:
            user_run = created_data["user_runs"][0]
            user_run_details = user_client.runs.get(id=user_run.id)
            if hasattr(user_run_details, 'created_by_user') and user_run_details.created_by_user:
                created_data["user_id"] = user_run_details.created_by_user.id
        
        if created_data["station_runs"]:
            station_run = created_data["station_runs"][0]
            station_run_details = station_client.runs.get(id=station_run.id)
            if hasattr(station_run_details, 'created_by_station') and station_run_details.created_by_station:
                created_data["station_id"] = station_run_details.created_by_station.id
        
        return created_data

    def test_filter_by_created_by_user_ids(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test filtering by created_by_user_ids."""
        user_id = test_runs_with_auth_info["user_id"]
        user_runs = test_runs_with_auth_info["user_runs"]
        
        # User ID should be available from runs created with user auth
        assert user_id is not None, "Could not determine user ID from created runs - this suggests a test setup issue"
        
        # Filter by the actual user ID
        result = client.runs.list(created_by_user_ids=[user_id])
        assert_get_runs_success(result)
        
        # Should find at least the runs we created with user auth
        user_run_ids = [run.id for run in user_runs]
        found_user_runs = [r for r in result.data if r.id in user_run_ids]
        assert len(found_user_runs) >= len(user_runs), f"Expected at least {len(user_runs)} user runs, found {len(found_user_runs)}"
        
        # All found runs should have been created by the user
        for run in found_user_runs:
            run_details = client.runs.get(id=run.id)
            assert run_details.created_by_user is not None
            if hasattr(run_details.created_by_user, 'id'):
                assert run_details.created_by_user.id == user_id  # type: ignore[union-attr]

    def test_filter_by_created_by_station_ids(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test filtering by created_by_station_ids."""
        station_id = test_runs_with_auth_info["station_id"]
        station_runs = test_runs_with_auth_info["station_runs"]
        
        # Station ID should be available from runs created with station auth
        assert station_id is not None, "Could not determine station ID from created runs - this suggests a test setup issue"
        
        # Filter by the actual station ID
        result = client.runs.list(created_by_station_ids=[station_id])
        assert_get_runs_success(result)
        
        # Should find at least the runs we created with station auth
        station_run_ids = [run.id for run in station_runs]
        found_station_runs = [r for r in result.data if r.id in station_run_ids]
        assert len(found_station_runs) >= len(station_runs), f"Expected at least {len(station_runs)} station runs, found {len(found_station_runs)}"
        
        # All found runs should have been created by the station
        for run in found_station_runs:
            run_details = client.runs.get(id=run.id)
            assert run_details.created_by_station is not None
            if hasattr(run_details.created_by_station, 'id'):
                assert run_details.created_by_station.id == station_id  # type: ignore[union-attr]

    def test_filter_by_operated_by_ids(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test filtering by operated_by_ids."""
        # For now, test with sample UUIDs as operated_by might be different from created_by
        result = client.runs.list(operated_by_ids=[
            "c84c1536-5d5f-11f0-8b95-dbf3626a9c22",
            "d1e2f3a4-5678-9abc-def1-23456789abcd"
        ])
        assert_get_runs_success(result)
        assert isinstance(result.data, list)

    def test_filter_by_single_user_id(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test filtering by single user ID."""
        user_id = test_runs_with_auth_info["user_id"]
        
        if user_id:
            result = client.runs.list(created_by_user_ids=[user_id])
            assert_get_runs_success(result)
            assert isinstance(result.data, list)
            # Should return at least some results
            assert len(result.data) >= 2, "Should find at least the 2 runs created with user auth"

    def test_empty_created_by_user_ids_filter(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test empty created_by_user_ids array behavior."""
        result_empty = client.runs.list(created_by_user_ids=[])
        result_no_param = client.runs.list()
        assert_get_runs_success(result_empty)
        assert_get_runs_success(result_no_param)
        
        # Empty array should behave same as no parameter
        assert len(result_empty.data) > 0
        assert len(result_empty.data) == len(result_no_param.data)

    def test_empty_created_by_station_ids_filter(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test empty created_by_station_ids array behavior."""
        result_empty = client.runs.list(created_by_station_ids=[])
        result_no_param = client.runs.list()
        assert_get_runs_success(result_empty)
        assert_get_runs_success(result_no_param)
        
        # Empty array should behave same as no parameter
        assert len(result_empty.data) > 0
        assert len(result_empty.data) == len(result_no_param.data)

    def test_empty_operated_by_ids_filter(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test empty operated_by_ids array behavior."""
        result_empty = client.runs.list(operated_by_ids=[])
        result_no_param = client.runs.list()
        assert_get_runs_success(result_empty)
        assert_get_runs_success(result_no_param)
        
        # Empty array should behave same as no parameter
        assert len(result_empty.data) > 0
        assert len(result_empty.data) == len(result_no_param.data)

    def test_nonexistent_user_ids(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test filtering by nonexistent user IDs."""
        # Use valid UUID format but IDs that don't exist
        result = client.runs.list(created_by_user_ids=[
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000002"
        ])
        assert_get_runs_success(result)
        assert isinstance(result.data, list)
        # Should return few or no results since these UUIDs likely don't exist

    def test_nonexistent_station_ids(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test filtering by nonexistent station IDs."""
        result = client.runs.list(created_by_station_ids=[
            "00000000-0000-0000-0000-000000000003",
            "00000000-0000-0000-0000-000000000004"
        ])
        assert_get_runs_success(result)
        assert isinstance(result.data, list)
        
    def test_combined_user_station_filters(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test combination of user and station filters.
        
        IMPORTANT: The backend uses AND logic for combining filters.
        When both created_by_user_ids and created_by_station_ids are provided,
        it looks for runs created by BOTH a user AND a station, which is impossible.
        A run can only be created by either a user OR a station, never both.
        """
        user_id = test_runs_with_auth_info["user_id"]
        station_id = test_runs_with_auth_info["station_id"]
        
        # Both user and station IDs should be available from the test fixture
        assert user_id is not None, "Could not determine user ID from created runs - this suggests a test setup issue"
        assert station_id is not None, "Could not determine station ID from created runs - this suggests a test setup issue"
        
        # Test the combined filter behavior (AND logic)
        result = client.runs.list(
            created_by_user_ids=[user_id],
            created_by_station_ids=[station_id],
        )
        assert_get_runs_success(result)
        assert isinstance(result.data, list)
        
        # The filters are combined with AND, so a run must be created by BOTH
        # a user AND a station, which is impossible. Expect 0 results.
        assert len(result.data) == 0, f"Expected 0 runs when filtering by both user and station IDs (AND logic), found {len(result.data)}"
        
        # Verify separately that each filter works independently
        user_only = client.runs.list(created_by_user_ids=[user_id])
        station_only = client.runs.list(created_by_station_ids=[station_id])
        
        assert len(user_only.data) >= 2, "Should find at least 2 user runs"
        assert len(station_only.data) >= 2, "Should find at least 2 station runs"
        
        # Document that to get runs from EITHER user OR station, must make separate requests
        # and combine results client-side
        all_runs = []  # type: ignore[var-annotated]
        user_run_ids = set(r.id for r in user_only.data)
        for run in station_only.data:
            if run.id not in user_run_ids:
                all_runs.append(run)  # type: ignore[arg-type]
        all_runs.extend(user_only.data)  # type: ignore[arg-type]
        
        # Verify we found all our test runs when combining results
        user_runs = test_runs_with_auth_info["user_runs"]
        station_runs = test_runs_with_auth_info["station_runs"]
        all_test_runs = user_runs + station_runs
        all_test_run_ids = [run.id for run in all_test_runs]  # type: ignore[attr-defined]
        found_test_runs = [r for r in all_runs if r.id in all_test_run_ids]  # type: ignore[attr-defined]
        assert len(found_test_runs) >= 4, f"When combining user and station results client-side, expected at least 4 runs, found {len(found_test_runs)}"  # type: ignore[arg-type]
    
    def test_multiple_user_ids_filter(self, client: TofuPilot, test_runs_with_auth_info: Dict[str, Any]) -> None:
        """Test filtering by multiple user IDs including actual and nonexistent."""
        user_id = test_runs_with_auth_info["user_id"]
        
        if user_id:
            # Mix real user ID with fake ones
            result = client.runs.list(created_by_user_ids=[
                user_id,
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002"
            ])
            assert_get_runs_success(result)
            
            # Should still find the user's runs
            user_runs = test_runs_with_auth_info["user_runs"]
            user_run_ids = [run.id for run in user_runs]
            found_user_runs = [r for r in result.data if r.id in user_run_ids]
            assert len(found_user_runs) >= len(user_runs)