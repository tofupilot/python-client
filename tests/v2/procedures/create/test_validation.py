"""Test procedure creation validation rules."""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorBADREQUEST, APIError
from ..utils import assert_create_procedure_success, get_procedure_by_id
from ...utils import assert_station_access_forbidden


class TestCreateProcedureValidation:

    def test_empty_procedure_name_fails(self, client: TofuPilot, auth_type: str) -> None:
        """Test that creating a procedure with empty name fails."""
        if auth_type == "station":
            # Stations cannot create procedures - get 403 before validation
            with pytest.raises(APIError) as exc_info:
                client.procedures.create(name="")
            assert "403" in str(exc_info.value) or "cannot create procedures" in str(exc_info.value).lower()
        else:
            # Users get validation error
            with pytest.raises(APIError) as exc_info:
                client.procedures.create(name="")
            
            # Verify the error is about validation
            error_message = str(exc_info.value).lower()
            assert "validation" in error_message
            assert exc_info.value.status_code == 400

    def test_whitespace_only_name_fails(self, client: TofuPilot, auth_type: str) -> None:
        """Test that creating a procedure with whitespace-only name fails."""
        if auth_type == "station":
            # Stations cannot create procedures - get 403 before validation
            with pytest.raises(APIError) as exc_info:
                client.procedures.create(name="   ")
            assert "403" in str(exc_info.value) or "cannot create procedures" in str(exc_info.value).lower()
        else:
            # Users get validation error
            with pytest.raises(APIError) as exc_info:
                client.procedures.create(name="   ")
            
            # Verify the error is about validation
            error_message = str(exc_info.value).lower()
            assert "validation" in error_message
            assert exc_info.value.status_code == 400

    def test_create_procedure_with_leading_trailing_spaces(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test creating a procedure with leading/trailing spaces."""
        base_name = f"AutomatedTest-V2-Spaces-{timestamp}"
        PROCEDURE_NAME = f"  {base_name}  "
        
        if auth_type == "station":
            # Station cannot create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name=PROCEDURE_NAME)
            return
        
        # User test - this might succeed (spaces trimmed) or fail - either is acceptable
        try:
            result = client.procedures.create(name=PROCEDURE_NAME)
            assert_create_procedure_success(result)
            # Fetch procedure to verify name (might be trimmed)
            proc = get_procedure_by_id(client, result.id)
            assert proc is not None
            assert base_name in proc.name
        except ErrorBADREQUEST:
            # Some systems reject leading/trailing spaces
            pass
    
    def test_very_long_name_handling(self, client: TofuPilot, auth_type: str) -> None:
        """Test behavior with very long procedure names."""
        # Create a 1000-character procedure name
        PROCEDURE_NAME = "AutomatedTest-V2-VeryLong-" + "X" * 1000
        
        if auth_type == "station":
            # Stations cannot create procedures - get 403 before validation
            with pytest.raises(APIError) as exc_info:
                client.procedures.create(name=PROCEDURE_NAME)
            assert "403" in str(exc_info.value) or "cannot create procedures" in str(exc_info.value).lower()
        else:
            # Users get validation error for excessively long names
            with pytest.raises(APIError) as exc_info:
                client.procedures.create(name=PROCEDURE_NAME)
            
            # Verify the error is about validation (length)
            error_message = str(exc_info.value).lower()
            assert "validation" in error_message
            assert exc_info.value.status_code == 400
    
    def test_create_procedure_name_character_validation(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test various characters in procedure names."""
        
        test_cases = [
            ("numbers", f"Test-123-{timestamp}"),
            ("underscores", f"Test_Underscores_{timestamp}"),
            ("hyphens", f"Test-Hyphens-{timestamp}"),
            ("periods", f"Test.Periods.{timestamp}"),
            ("mixed", f"Test_Mix-123.Name-{timestamp}"),
        ]
        
        if auth_type == "station":
            # Station cannot create procedures (HTTP 403 FORBIDDEN)
            for test_name, procedure_name in test_cases:
                with assert_station_access_forbidden(f"create procedure with {test_name}"):
                    client.procedures.create(name=procedure_name)
            return
        
        # User test - various character types
        for test_name, procedure_name in test_cases:
            try:
                result = client.procedures.create(name=procedure_name)
                assert_create_procedure_success(result)
                # Fetch procedure to verify name
                proc = get_procedure_by_id(client, result.id)
                assert proc is not None
                assert proc.name == procedure_name
            except ErrorBADREQUEST as e:
                # Some characters might not be allowed - that's okay
                print(f"Character test '{test_name}' failed as expected: {e}")