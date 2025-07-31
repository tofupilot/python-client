"""Test procedure deletion."""

from datetime import datetime, timezone
from typing import List
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_procedure_success, assert_delete_procedure_success, assert_get_procedures_success
from ...utils import assert_station_access_forbidden


class TestDeleteProcedure:

    def test_delete_empty_procedure_success(self, client: TofuPilot, auth_type: str) -> None:
        """Test successfully deleting an empty procedure."""
        PROCEDURE_NAME = f"AutomatedTest-V2-Delete-Empty-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "station":
            # Station should fail to delete procedures (HTTP 403 FORBIDDEN)
            fake_procedure_id = "12345678-1234-1234-1234-123456789abc"
            
            with assert_station_access_forbidden("delete procedure"):
                client.procedures.delete(id=fake_procedure_id)
            return
            
        # User API can create and delete procedures
        create_result = client.procedures.create(name=PROCEDURE_NAME)
        assert_create_procedure_success(create_result)
        procedure_id = create_result.id
        
        # Delete the procedure
        delete_result = client.procedures.delete(id=procedure_id)
        assert_delete_procedure_success(delete_result)
        assert delete_result.id == procedure_id
        
        # Verify procedure no longer exists in search
        list_result = client.procedures.list(search_query=PROCEDURE_NAME)
        assert_get_procedures_success(list_result)
        found_procedures = [p for p in list_result.data if p.id == procedure_id]
        assert len(found_procedures) == 0

    def test_delete_non_existent_procedure(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting a non-existent procedure returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        if auth_type == "station":
            # Station should fail to delete procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete procedure"):
                client.procedures.delete(id=fake_id)
            return
            
        # User API test - should get error for non-existent procedure
        with pytest.raises(ErrorNOTFOUND) as exc_info:
            client.procedures.delete(id=fake_id)
        
        # Should be not found error (404 or 500 with not found message)
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "404", "does not exist"])

    def test_delete_already_deleted_procedure(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting an already deleted procedure fails."""
        PROCEDURE_NAME = f"AutomatedTest-V2-Delete-Twice-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "station":
            # Station should fail to delete procedures (HTTP 403 FORBIDDEN)
            fake_procedure_id = "12345678-1234-1234-1234-123456789abc"
            
            with assert_station_access_forbidden("delete procedure"):
                client.procedures.delete(id=fake_procedure_id)
            return
            
        # User API test - create, delete, then try to delete again
        create_result = client.procedures.create(name=PROCEDURE_NAME)
        assert_create_procedure_success(create_result)
        procedure_id = create_result.id
        
        # First deletion should succeed
        delete_result = client.procedures.delete(id=procedure_id)
        assert_delete_procedure_success(delete_result)
        
        # Second deletion should fail
        with pytest.raises(ErrorNOTFOUND) as exc_info:
            client.procedures.delete(id=procedure_id)
        
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "404", "does not exist"])

    def test_create_delete_recreate_same_name(self, client: TofuPilot, auth_type: str) -> None:
        """Test that after deleting a procedure, the same name can be reused."""
        PROCEDURE_NAME = f"AutomatedTest-V2-Recreate-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=PROCEDURE_NAME)
            return
            
        # User API can create and delete procedures
        # Create first procedure
        result1 = client.procedures.create(name=PROCEDURE_NAME)
        assert_create_procedure_success(result1)
        
        # Delete it
        delete_result = client.procedures.delete(id=result1.id)
        assert_delete_procedure_success(delete_result)
        
        # Create new procedure with same name - should succeed
        result2 = client.procedures.create(name=PROCEDURE_NAME)
        assert_create_procedure_success(result2)
        assert result2.id != result1.id  # Should be different procedure
        
        # Verify via search that the procedure has the correct name
        list_result = client.procedures.list(search_query=PROCEDURE_NAME)
        assert_get_procedures_success(list_result)
        found_procedures = [p for p in list_result.data if p.id == result2.id]
        assert len(found_procedures) == 1
        assert found_procedures[0].name == PROCEDURE_NAME

    # REMOVED: test_delete_procedure_with_runs_warning
    # This test was deleting the shared procedure_id fixture used by other tests,
    # causing cascading failures. Delete operations should create their own test procedures.

    def test_multiple_procedure_deletions(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting multiple procedures."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=f"AutomatedTest-V2-Delete-Multi-{timestamp}-0")
            return
            
        # User API can create and delete procedures
        procedure_ids: List[str] = []
        
        # Create multiple procedures
        for i in range(3):
            procedure = client.procedures.create(
                name=f"AutomatedTest-V2-Delete-Multi-{timestamp}-{i}"
            )
            assert_create_procedure_success(procedure)
            procedure_ids.append(procedure.id)
        
        # Delete all procedures
        for procedure_id in procedure_ids:
            delete_result = client.procedures.delete(id=procedure_id)
            assert_delete_procedure_success(delete_result)
            assert delete_result.id == procedure_id
        
        # Verify all are gone
        for procedure_id in procedure_ids:
            with pytest.raises(ErrorNOTFOUND):
                client.procedures.update(id=procedure_id, name="Should-Not-Work")

    def test_delete_updated_procedure(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting a procedure after updating it."""
        original_name = f"DelUpd-Orig-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=original_name)
            return
            
        # User API can create, update, and delete procedures
        # Create a procedure
        create_result = client.procedures.create(name=original_name)
        assert_create_procedure_success(create_result)
        
        # Update the procedure
        new_name = f"DelUpd-Mod-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        update_result = client.procedures.update(id=create_result.id, name=new_name)
        from ..utils import assert_update_procedure_success
        assert_update_procedure_success(update_result)
        
        # Delete the procedure
        delete_result = client.procedures.delete(id=create_result.id)
        assert_delete_procedure_success(delete_result)
        
        # Verify it's gone
        list_result = client.procedures.list(search_query=new_name)
        assert_get_procedures_success(list_result)
        found_procedures = [p for p in list_result.data if p.id == create_result.id]
        assert len(found_procedures) == 0

    def test_delete_procedure_lifecycle(self, client: TofuPilot, auth_type: str) -> None:
        """Test complete procedure lifecycle: create, update, delete."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        if auth_type == "station":
            # Station should fail to create procedures (HTTP 403 FORBIDDEN)
            original_name = f"AutomatedTest-V2-Lifecycle-Original-{timestamp}"
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=original_name)
            return
            
        # User API can create, update, and delete procedures
        # Create
        original_name = f"AutomatedTest-V2-Lifecycle-Original-{timestamp}"
        create_result = client.procedures.create(name=original_name)
        assert_create_procedure_success(create_result)
        
        # Update
        updated_name = f"AutomatedTest-V2-Lifecycle-Updated-{timestamp}"
        update_result = client.procedures.update(id=create_result.id, name=updated_name)
        from ..utils import assert_update_procedure_success
        assert_update_procedure_success(update_result)
        
        # Verify it exists with new name
        list_result = client.procedures.list(search_query=updated_name)
        assert_get_procedures_success(list_result)
        found = any(p.id == create_result.id for p in list_result.data)
        assert found
        
        # Delete
        delete_result = client.procedures.delete(id=create_result.id)
        assert_delete_procedure_success(delete_result)
        
        # Verify it's gone
        list_result = client.procedures.list(search_query=updated_name)
        assert_get_procedures_success(list_result)
        found = any(p.id == create_result.id for p in list_result.data)
        assert not found