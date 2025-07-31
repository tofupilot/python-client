"""Test basic procedure creation."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_procedure_success, assert_get_procedures_success, get_procedure_by_id
from ...utils import assert_station_access_forbidden


class TestCreateProcedureMinimal:

    def test_create_procedure_with_simple_name(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a procedure with a simple name."""
        PROCEDURE_NAME = f"AutomatedTest-V2-Create-Simple-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "station":
            # Station should fail to create procedures with HTTP 403 FORBIDDEN
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=PROCEDURE_NAME)
            return
            
        # User API can create procedures
        result = client.procedures.create(name=PROCEDURE_NAME)
        
        # Verify successful response
        assert_create_procedure_success(result)
        
        # Fetch procedure to verify name
        proc = get_procedure_by_id(client, result.id)
        assert proc is not None
        assert proc.name == PROCEDURE_NAME
        
        # Test procedures.list to verify it's in the list
        # Try both search and general list to handle potential timing issues
        list_result = client.procedures.list(search_query=PROCEDURE_NAME)
        assert_get_procedures_success(list_result)
        
        # Check if found in search results
        found_in_search = any(p.id == result.id for p in list_result.data)
        
        if not found_in_search:
            # If not found in search, check general list (timing issue workaround)
            general_list = client.procedures.list(limit=50)
            assert_get_procedures_success(general_list)
            found_in_general = any(p.id == result.id for p in general_list.data)
            assert found_in_general, f"Procedure {result.id} not found in search or general list"
    
    def test_create_procedure_with_long_name(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a procedure with a long name."""
        # Create a long but valid procedure name (within validation limits)
        base_name = f"AutomatedTest-V2-Create-Long-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        PROCEDURE_NAME = base_name + "-LONG"  # Keep under 100 chars total
        
        if auth_type == "station":
            # Station should fail to create procedures with HTTP 403 FORBIDDEN
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=PROCEDURE_NAME)
            return
            
        # User API can create procedures
        result = client.procedures.create(name=PROCEDURE_NAME)
        
        # Verify successful response
        assert_create_procedure_success(result)
        
        # Fetch procedure to verify name
        proc = get_procedure_by_id(client, result.id)
        assert proc is not None
        assert proc.name == PROCEDURE_NAME
    
    def test_create_procedure_with_special_characters(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a procedure with special characters in name."""
        PROCEDURE_NAME = f"AutomatedTest-V2-Special-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}-!@#$%^&*()"
        
        if auth_type == "station":
            # Station should fail to create procedures with HTTP 403 FORBIDDEN
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=PROCEDURE_NAME)
            return
            
        # User API can create procedures
        result = client.procedures.create(name=PROCEDURE_NAME)
        
        # Verify successful response
        assert_create_procedure_success(result)
        
        # Fetch procedure to verify name
        proc = get_procedure_by_id(client, result.id)
        assert proc is not None
        assert proc.name == PROCEDURE_NAME
    
    def test_create_procedure_with_unicode(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a procedure with unicode characters."""
        PROCEDURE_NAME = f"AutomatedTest-V2-Unicode-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}-测试-café-🚀"
        
        if auth_type == "station":
            # Station should fail to create procedures with HTTP 403 FORBIDDEN
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=PROCEDURE_NAME)
            return
            
        # User API can create procedures
        result = client.procedures.create(name=PROCEDURE_NAME)
        
        # Verify successful response
        assert_create_procedure_success(result)
        
        # Fetch procedure to verify name
        proc = get_procedure_by_id(client, result.id)
        assert proc is not None
        assert proc.name == PROCEDURE_NAME