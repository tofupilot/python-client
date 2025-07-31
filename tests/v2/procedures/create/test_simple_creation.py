"""Test simple procedure creation without search dependency."""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_procedure_success, get_procedure_by_id
from ...utils import assert_station_access_forbidden


class TestSimpleProcedureCreation:

    def test_create_procedure_basic(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a procedure - behavior differs by auth type.
        
        Users: Can create procedures successfully.
        Stations: Cannot create procedures (access policy restriction).
        """
        PROCEDURE_NAME = f"AutomatedTest-V2-Simple-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "user":
            # Users can create procedures
            result = client.procedures.create(name=PROCEDURE_NAME)
            
            # Verify successful response
            assert_create_procedure_success(result)
            
            # Fetch procedure to verify name
            proc = get_procedure_by_id(client, result.id)
            assert proc is not None
            assert proc.name == PROCEDURE_NAME
            
            # Just verify we can list procedures (no search required)
            list_result = client.procedures.list(limit=10)
            assert hasattr(list_result, 'data')
            assert isinstance(list_result.data, list)
            
            # Check if our procedure appears in the general list
            procedure_found = any(p.id == result.id for p in list_result.data)
            if not procedure_found:
                # If not in first 10, that's okay - just print for debugging
                print(f"Note: Created procedure {result.id} not in first 10 results (expected for active systems)")
        else:
            # Stations cannot create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=PROCEDURE_NAME)

    def test_create_and_update_procedure(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating and updating a procedure - behavior differs by auth type.
        
        Users: Can create and update procedures.
        Stations: Cannot create or update procedures (access policy restriction).
        """
        original_name = f"AutomatedTest-V2-CreateUpdate-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "user":
            # Users can create and update procedures
            create_result = client.procedures.create(name=original_name)
            assert_create_procedure_success(create_result)
            
            # Update
            new_name = f"AutomatedTest-V2-Updated-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
            from ..utils import assert_update_procedure_success
            update_result = client.procedures.update(id=create_result.id, name=new_name)
            assert_update_procedure_success(update_result)
            assert update_result.id == create_result.id
        else:
            # Stations cannot create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=original_name)

    def test_create_and_delete_procedure(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating and deleting a procedure - behavior differs by auth type.
        
        Users: Can create and delete procedures.
        Stations: Cannot create or delete procedures (access policy restriction).
        """
        procedure_name = f"AutomatedTest-V2-CreateDelete-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "user":
            # Users can create and delete procedures
            create_result = client.procedures.create(name=procedure_name)
            assert_create_procedure_success(create_result)
            
            # Delete
            from ..utils import assert_delete_procedure_success
            delete_result = client.procedures.delete(id=create_result.id)
            assert_delete_procedure_success(delete_result)
            assert delete_result.id == create_result.id
        else:
            # Stations cannot create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=procedure_name)