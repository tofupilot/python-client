"""Test station access control for procedure creation.

This test verifies that the x-access middleware properly rejects procedure creation
requests from stations with the correct HTTP status code and error message.

Based on the OpenAPI x-access definition:
- level: 'unauthorized'
- type: 'station' 
- description: 'Stations cannot create procedures'
"""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError


class TestStationAccessControl:

    def test_station_cannot_create_procedure_with_proper_http_error(self, client: TofuPilot, auth_type: str) -> None:
        """Test that stations receive proper HTTP 403 FORBIDDEN error when attempting to create procedures."""
        PROCEDURE_NAME = f"AccessControl-Test-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "user":
            # Users should be able to create procedures - verify this works
            result = client.procedures.create(name=PROCEDURE_NAME)
            assert hasattr(result, 'id')
            assert isinstance(result.id, str)
            assert len(result.id) > 0
            return
            
        # Station should receive 403 FORBIDDEN error
        assert auth_type == "station", f"Expected station auth type, got: {auth_type}"
        
        with pytest.raises(APIError) as exc_info:
            client.procedures.create(name=PROCEDURE_NAME)
        
        # Verify the HTTP status code is 403 FORBIDDEN
        api_error = exc_info.value
        assert hasattr(api_error, 'status_code'), f"APIError should have status_code attribute. Error: {api_error}"
        assert api_error.status_code == 403, f"Expected HTTP 403 FORBIDDEN, got: {api_error.status_code}. Full error: {api_error}"
        
        # Verify the error message indicates access control failure
        error_message = str(api_error).lower()
        access_control_keywords = [
            "stations cannot create procedures",  # Our exact x-access description
            "station access is not authorized",   # Generic middleware message
            "forbidden",                          # HTTP status meaning
            "access denied for station",         # Middleware message for missing rule
        ]
        
        assert any(keyword in error_message for keyword in access_control_keywords), (
            f"Expected access control error message containing one of {access_control_keywords}, "
            f"but got: {api_error}"
        )

    def test_station_access_control_error_structure(self, client: TofuPilot, auth_type: str) -> None:
        """Test that the error response has the expected structure for debugging."""
        if auth_type == "user":
            return  # Users can create procedures, so no error to test
            
        PROCEDURE_NAME = f"ErrorStructure-Test-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        with pytest.raises(APIError) as exc_info:
            client.procedures.create(name=PROCEDURE_NAME)
        
        api_error = exc_info.value
        
        # Verify error has proper structure for debugging
        assert hasattr(api_error, 'status_code'), "APIError should have status_code"
        assert api_error.status_code == 403, f"Expected 403, got {api_error.status_code}"
        
        # The error should provide meaningful information
        error_str = str(api_error)
        assert len(error_str) > 0, "Error message should not be empty"
        
        # Should not contain internal implementation details that could be security risks
        internal_keywords = ["stack", "traceback", "file", "line"]
        error_lower = error_str.lower()
        for keyword in internal_keywords:
            assert keyword not in error_lower, f"Error should not expose internal details: {keyword}"

    def test_different_station_operations_same_error_pattern(self, client: TofuPilot, auth_type: str) -> None:
        """Test that different unauthorized station operations follow the same error pattern."""
        if auth_type == "user":
            return  # Users can create procedures, so no error to test
            
        # Test procedure creation (should fail)
        PROCEDURE_NAME = f"Pattern-Test-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        with pytest.raises(APIError) as create_exc:
            client.procedures.create(name=PROCEDURE_NAME)
        
        create_error = create_exc.value
        assert create_error.status_code == 403
        
        # All unauthorized station operations should return 403 with meaningful messages
        assert hasattr(create_error, 'status_code')
        assert isinstance(create_error.status_code, int)
        
        # Error message should be user-friendly, not a technical stack trace
        error_msg = str(create_error)
        assert len(error_msg) > 10, "Error message should be descriptive"
        assert "station" in error_msg.lower() or "forbidden" in error_msg.lower(), (
            f"Error should mention access issue: {error_msg}"
        )