"""Test basic part operations."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ..utils import assert_station_access_forbidden


class TestParts:
    
    def test_create_part(self, client: TofuPilot) -> None:
        """Test creating a new part."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"TEST-BASIC-001-{timestamp}"
        result = client.parts.create(number=part_number, name="Test Part")
        
        assert hasattr(result, 'id')
        assert isinstance(result.id, str)
        assert len(result.id) > 0
        
        # Verify by listing the part
        list_result = client.parts.list(search_query=part_number)
        assert len(list_result.data) >= 1
        part = next((p for p in list_result.data if p.id == result.id), None)
        assert part is not None
        assert part.number == part_number
        assert part.name == "Test Part"
    
    def test_create_part_with_revision(self, client: TofuPilot) -> None:
        """Test creating a new part with revision."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"TEST-BASIC-002-{timestamp}"
        result = client.parts.create(
            number=part_number,
            name="Test Part with Revision",
            revision_number="v1.0"
        )
        
        assert hasattr(result, 'id')
        assert isinstance(result.id, str)
        assert len(result.id) > 0
        
        # Verify by listing the part
        list_result = client.parts.list(search_query=part_number)
        assert len(list_result.data) >= 1
        part = next((p for p in list_result.data if p.id == result.id), None)
        assert part is not None
        assert part.number == part_number
        assert part.name == "Test Part with Revision"
        assert len(part.revisions) == 1
        assert part.revisions[0].number == "v1.0"
    
    def test_list_parts(self, client: TofuPilot) -> None:
        """Test listing parts."""
        result = client.parts.list()
        
        assert hasattr(result, 'data')
        assert isinstance(result.data, list)
    
    def test_list_parts_with_filters(self, client: TofuPilot) -> None:
        """Test listing parts with filters."""
        result = client.parts.list(
            limit=10,
            search_query="test"
        )
        
        assert hasattr(result, 'data')
        assert isinstance(result.data, list)
    
    def test_update_part(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating a part."""
        # First create a part
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"TEST-BASIC-003-{timestamp}"
        create_result = client.parts.create(number=part_number, name="Test Part for Update")
        part_id = create_result.id
        
        if auth_type == "station":
            # Station should receive HTTP 403 FORBIDDEN when trying to update parts
            with assert_station_access_forbidden("update part"):
                client.parts.update(
                    number=part_number,
                    name="Updated Test Part"
                )
        else:
            # Then update it
            result = client.parts.update(
                number=part_number,
                name="Updated Test Part"
            )
            
            assert hasattr(result, 'id')
            assert hasattr(result, 'number')
            assert hasattr(result, 'name')
            assert result.id == part_id
            assert result.name == "Updated Test Part"