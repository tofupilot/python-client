"""Test procedure name updates."""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND, ErrorBADREQUEST
from ..utils import assert_create_procedure_success, assert_update_procedure_success, assert_get_procedures_success
from ...utils import assert_station_access_forbidden


class TestUpdateProcedureName:
    
    def _expect_station_create_failure(self, client: TofuPilot, name: str) -> None:
        """Helper to verify stations cannot create procedures."""
        with assert_station_access_forbidden("create procedure"):
            client.procedures.create(name=name)

    def test_update_procedure_name_success(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test successfully updating a procedure's name."""
        if auth_type == "station":
            # Stations cannot create procedures (HTTP 403 FORBIDDEN)
            original_name = f"AutomatedTest-V2-Update-Original-{timestamp}"
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=original_name)
        else:
            # Users can create and update procedures
            # Create a procedure
            original_name = f"AutomatedTest-V2-Update-Original-{timestamp}"
            create_result = client.procedures.create(name=original_name)
            assert_create_procedure_success(create_result)
            
            # Update the procedure name
            new_name = f"AutomatedTest-V2-Update-Modified-{timestamp}"
            update_result = client.procedures.update(id=create_result.id, name=new_name)
            assert_update_procedure_success(update_result)
            assert update_result.id == create_result.id
            
            # Verify the name was updated by listing
            list_result = client.procedures.list(search_query=new_name)
            assert_get_procedures_success(list_result)
            found_procedure = next((p for p in list_result.data if p.id == create_result.id), None)
            assert found_procedure is not None
            assert found_procedure.name == new_name

    def test_update_procedure_name_with_special_characters(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating procedure name with special characters."""
        if auth_type == "station":
            # Stations cannot create procedures
            original_name = f"UpdSpec-{timestamp}"
            self._expect_station_create_failure(client, original_name)
        else:
            # Create a procedure
            original_name = f"UpdSpec-{timestamp}"
            create_result = client.procedures.create(name=original_name)
            assert_create_procedure_success(create_result)
            
            # Update with special characters
            new_name = f"UpdSpec-{timestamp}-!@#"
            update_result = client.procedures.update(id=create_result.id, name=new_name)
            assert_update_procedure_success(update_result)
            
            # Verify update worked
            list_result = client.procedures.list(search_query="UpdSpec")
            assert_get_procedures_success(list_result)
            found_procedure = next((p for p in list_result.data if p.id == create_result.id), None)
            assert found_procedure is not None
            assert found_procedure.name == new_name

    def test_update_procedure_name_with_unicode(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating procedure name with unicode characters."""
        if auth_type == "station":
            # Stations cannot create procedures
            original_name = f"UpdUni-{timestamp}"
            self._expect_station_create_failure(client, original_name)
        else:
            # Create a procedure
            original_name = f"UpdUni-{timestamp}"
            create_result = client.procedures.create(name=original_name)
            assert_create_procedure_success(create_result)
            
            # Update with unicode characters  
            new_name = f"UpdUni-{timestamp}-测试-café"
            update_result = client.procedures.update(id=create_result.id, name=new_name)
            assert_update_procedure_success(update_result)
            
            # Verify update worked
            list_result = client.procedures.list(search_query="UpdUni")
            assert_get_procedures_success(list_result)
            found_procedure = next((p for p in list_result.data if p.id == create_result.id), None)
            assert found_procedure is not None
            assert found_procedure.name == new_name

    def test_update_non_existent_procedure_fails(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating a non-existent procedure fails."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        new_name = f"AutomatedTest-V2-Update-NonExistent-{timestamp}"
        
        if auth_type == "station":
            with assert_station_access_forbidden("update procedure"):
                client.procedures.update(id=fake_id, name=new_name)
            return

        # Should return 404 for non-existent procedure
        with pytest.raises(ErrorNOTFOUND) as exc_info:
            client.procedures.update(id=fake_id, name=new_name)

        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "404", "does not exist", "procedure with id"])

    def test_update_procedure_empty_name_fails(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating procedure with empty name fails."""
        if auth_type == "station":
            # Stations cannot create procedures
            original_name = f"AutomatedTest-V2-Update-EmptyName-{timestamp}"
            self._expect_station_create_failure(client, original_name)
        else:
            # Create a procedure
            original_name = f"AutomatedTest-V2-Update-EmptyName-{timestamp}"
            create_result = client.procedures.create(name=original_name)
            assert_create_procedure_success(create_result)
            
            # Try to update with empty name
            with pytest.raises(ErrorBADREQUEST) as exc_info:
                client.procedures.update(id=create_result.id, name="")
            
            # Verify it's a validation error
            error_message = str(exc_info.value).lower()
            assert any(keyword in error_message for keyword in ["empty", "required", "name", "invalid", "validation"])

    def test_update_procedure_duplicate_name_succeeds(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating procedure to existing name succeeds (names are not unique)."""
        if auth_type == "station":
            # Stations cannot create procedures
            name1 = f"AutomatedTest-V2-Update-Duplicate1-{timestamp}"
            self._expect_station_create_failure(client, name1)
        else:
            
            # Create two procedures
            name1 = f"AutomatedTest-V2-Update-Duplicate1-{timestamp}"
            name2 = f"AutomatedTest-V2-Update-Duplicate2-{timestamp}"
            
            create_result1 = client.procedures.create(name=name1)
            create_result2 = client.procedures.create(name=name2)
            assert_create_procedure_success(create_result1)
            assert_create_procedure_success(create_result2)
            
            # Update second procedure to have same name as first - should succeed
            update_result = client.procedures.update(id=create_result2.id, name=name1)
            assert_update_procedure_success(update_result)
            assert update_result.id == create_result2.id
            
            # Both procedures should now have the same name (duplicate names allowed)
            # Verify by checking the update was successful
            assert update_result.id == create_result2.id

    def test_update_procedure_same_name_succeeds(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating procedure to the same name succeeds (no-op)."""
        if auth_type == "station":
            # Stations cannot create procedures
            original_name = f"AutomatedTest-V2-Update-SameName-{timestamp}"
            self._expect_station_create_failure(client, original_name)
        else:
            # Create a procedure
            original_name = f"AutomatedTest-V2-Update-SameName-{timestamp}"
            create_result = client.procedures.create(name=original_name)
            assert_create_procedure_success(create_result)
            
            # Update to the same name
            update_result = client.procedures.update(id=create_result.id, name=original_name)
            assert_update_procedure_success(update_result)
            assert update_result.id == create_result.id

    def test_update_procedure_long_name(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating procedure with long name."""
        if auth_type == "station":
            # Stations cannot create procedures
            original_name = f"AutomatedTest-V2-Update-LongName-{timestamp}"
            self._expect_station_create_failure(client, original_name)
        else:
            # Create a procedure
            original_name = f"AutomatedTest-V2-Update-LongName-{timestamp}"
            create_result = client.procedures.create(name=original_name)
            assert_create_procedure_success(create_result)
            
            # Update with long name
            base_name = f"AutomatedTest-V2-Update-VeryLong-{timestamp}"
            long_name = base_name + "-" + "X" * (200 - len(base_name))
            
            try:
                update_result = client.procedures.update(id=create_result.id, name=long_name)
                assert_update_procedure_success(update_result)
            except ErrorBADREQUEST as e:
                # Long names might be rejected - that's acceptable
                error_message = str(e).lower()
                assert any(keyword in error_message for keyword in ["length", "long", "limit", "validation"])

    def test_multiple_updates_same_procedure(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test multiple sequential updates to the same procedure."""
        if auth_type == "station":
            # Stations cannot create procedures
            original_name = f"UpdMult-{timestamp}"
            self._expect_station_create_failure(client, original_name)
        else:
            # Create a procedure
            original_name = f"UpdMult-{timestamp}"
            create_result = client.procedures.create(name=original_name)
            assert_create_procedure_success(create_result)
            
            # Perform multiple updates
            names = [
                f"UpdMult-Step1-{timestamp}",
                f"UpdMult-Step2-{timestamp}",
                f"UpdMult-Final-{timestamp}",
            ]
            
            for name in names:
                update_result = client.procedures.update(id=create_result.id, name=name)
                assert_update_procedure_success(update_result)
                assert update_result.id == create_result.id
            
            # Verify final name
            list_result = client.procedures.list(search_query="UpdMult-Final")
            assert_get_procedures_success(list_result)
            found_procedure = next((p for p in list_result.data if p.id == create_result.id), None)
            assert found_procedure is not None
            assert found_procedure.name == names[-1]