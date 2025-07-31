"""Test basic procedure operations."""

import pytest
import tofupilot
from .utils import get_procedure_by_id
from ..utils import assert_station_access_forbidden


class TestProcedures:
    
    def test_create_procedure(self, client: tofupilot.v2.TofuPilot, auth_type: str):
        """Test creating a new procedure."""
        if auth_type == "station":
            # Stations cannot create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name="Test Procedure")
        else:
            # Users can create procedures
            result = client.procedures.create(name="Test Procedure")
            
            assert hasattr(result, 'id')
            
            # Fetch procedure to verify name
            proc = get_procedure_by_id(client, result.id)
            assert proc is not None
            assert proc.name == "Test Procedure"
    
    def test_list_procedures(self, client: tofupilot.v2.TofuPilot):
        """Test listing procedures."""
        result = client.procedures.list()
        
        assert hasattr(result, 'data')
        assert isinstance(result.data, list)
    
    def test_list_procedures_with_filters(self, client: tofupilot.v2.TofuPilot):
        """Test listing procedures with filters."""
        result = client.procedures.list(
            limit=10,
            search_query="test"
        )
        
        assert hasattr(result, 'data')
        assert isinstance(result.data, list)
    
    def test_update_procedure(self, client: tofupilot.v2.TofuPilot, auth_type: str):
        """Test updating a procedure."""
        if auth_type == "station":
            # Stations cannot create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name="Test Procedure for Update")
        else:
            # Users can create and update procedures
            # First create a procedure
            create_result = client.procedures.create(name="Test Procedure for Update")
            procedure_id = create_result.id
            
            # Then update it
            result = client.procedures.update(
                id=procedure_id,
                name="Updated Test Procedure"
            )
            
            assert hasattr(result, 'id')
            assert result.id == procedure_id
        
            # Fetch procedure to verify name was updated
            proc = get_procedure_by_id(client, result.id)
            assert proc is not None
            assert proc.name == "Updated Test Procedure"
    
    def test_delete_procedure(self, client: tofupilot.v2.TofuPilot, auth_type: str):
        """Test deleting a procedure."""
        if auth_type == "station":
            # Stations cannot create procedures (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("create procedure"):
                client.procedures.create(name="Test Procedure for Delete")
        else:
            # Users can create and delete procedures
            # First create a procedure
            create_result = client.procedures.create(name="Test Procedure for Delete")
            procedure_id = create_result.id
            
            # Then delete it
            result = client.procedures.delete(id=procedure_id)
            
            # Should not raise an exception
            assert result is not None