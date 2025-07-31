"""Test duplicate procedure name handling."""

from datetime import datetime, timezone
from typing import List
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_procedure_success
from ...utils import assert_station_access_forbidden


class TestCreateProcedureDuplicateName:

    def test_duplicate_procedure_name_succeeds(self, client: TofuPilot, auth_type: str) -> None:
        """Test that creating procedures with duplicate names succeeds (names are not unique)."""
        PROCEDURE_NAME = f"AutomatedTest-V2-Duplicate-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=PROCEDURE_NAME)
            return
            
        # User API can create procedures
        # Create first procedure
        result1 = client.procedures.create(name=PROCEDURE_NAME)
        assert_create_procedure_success(result1)
        
        # Create second procedure with same name - should succeed per schema
        result2 = client.procedures.create(name=PROCEDURE_NAME)
        assert_create_procedure_success(result2)
        
        # Verify they are different procedures (different IDs)
        assert result1.id != result2.id
        
        # Fetch procedures to verify names
        procedures = client.procedures.list(limit=100)
        proc1 = next((p for p in procedures.data if p.id == result1.id), None)
        proc2 = next((p for p in procedures.data if p.id == result2.id), None)
        
        assert proc1 is not None
        assert proc2 is not None
        
        # Both should have the same name (duplicate names allowed)
        assert proc1.name == proc2.name == PROCEDURE_NAME
    
    def test_case_sensitivity_in_names(self, client: TofuPilot, auth_type: str) -> None:
        """Test case sensitivity in procedure names."""
        base_name = f"AutomatedTest-V2-Case-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        PROCEDURE_NAME_LOWER = base_name.lower()
        PROCEDURE_NAME_UPPER = base_name.upper()
        
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=PROCEDURE_NAME_LOWER)
            return
            
        # User API can create procedures
        # Create procedure with lowercase
        result1 = client.procedures.create(name=PROCEDURE_NAME_LOWER)
        assert_create_procedure_success(result1)
        
        # Create procedure with uppercase - should always succeed (no uniqueness constraint)
        result2 = client.procedures.create(name=PROCEDURE_NAME_UPPER)
        assert_create_procedure_success(result2)
        
        # Verify they are different procedures with different names
        assert result1.id != result2.id
        
        # Fetch procedures to verify names
        procedures = client.procedures.list(limit=100)
        proc1 = next((p for p in procedures.data if p.id == result1.id), None)
        proc2 = next((p for p in procedures.data if p.id == result2.id), None)
        
        assert proc1 is not None
        assert proc2 is not None
        assert proc1.name == PROCEDURE_NAME_LOWER
        assert proc2.name == PROCEDURE_NAME_UPPER
    
    def test_similar_but_different_names_succeed(self, client: TofuPilot, auth_type: str) -> None:
        """Test that similar but different names can be created."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        names = [
            f"AutomatedTest-V2-Similar-{timestamp}-A",
            f"AutomatedTest-V2-Similar-{timestamp}-B",
            f"AutomatedTest-V2-Similar-{timestamp}-1",
            f"AutomatedTest-V2-Similar-{timestamp}-2",
        ]
        
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=names[0])
            return
            
        # User API can create procedures
        created_procedures: List[models.ProcedureCreateResponse] = []
        expected_names: List[str] = []
        for name in names:
            result = client.procedures.create(name=name)
            assert_create_procedure_success(result)
            created_procedures.append(result)
            expected_names.append(name)
        
        # Verify all procedures have unique IDs
        ids: List[str] = [p.id for p in created_procedures]
        assert len(ids) == len(set(ids))  # All unique
        
        # Fetch procedures to verify names
        procedures = client.procedures.list(limit=100)
        for i, created in enumerate(created_procedures):
            proc = next((p for p in procedures.data if p.id == created.id), None)
            assert proc is not None
            assert proc.name == expected_names[i]