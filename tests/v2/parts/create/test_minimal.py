"""Test minimal part creation."""

from datetime import datetime, timezone
import uuid
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_part_success, assert_get_parts_success


class TestCreatePartMinimal:
    """Test minimal part creation scenarios."""
    
    def test_create_part_number_only(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a part with only required fields (number)."""
            
        # Test constants - ensure uniqueness with timestamp + uuid + random
        import time
        import random
        timestamp_ms = int(time.time() * 1000)
        unique_id = str(uuid.uuid4()).replace('-', '')[:12]
        random_suffix = random.randint(1000, 9999)
        PART_NUMBER = f"PYTEST-{timestamp_ms}-{unique_id}-{random_suffix}"
        
        # Create part using SDK
        result = client.parts.create(
            number=PART_NUMBER,
        )
        
        # Verify successful response
        assert_create_part_success(result)
        
        # Test parts.list to verify it's in the list
        list_result = client.parts.list(search_query=PART_NUMBER)
        assert_get_parts_success(list_result)
        assert len(list_result.data) >= 1
        
        # Find our created part
        found_part = None
        for part in list_result.data:
            if part.number == PART_NUMBER:
                found_part = part
                break
        
        assert found_part is not None
        assert found_part.id == result.id
        assert found_part.number == PART_NUMBER
        # When name is not provided, API defaults to "New Part"
        assert found_part.name == "New Part"
        # Should have one revision with default identifier "A"
        assert len(found_part.revisions) == 1
        assert found_part.revisions[0].number == "A"
    
    def test_create_part_with_name(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a part with number and name."""
            
        # Test constants - ensure uniqueness with uuid
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        PART_NUMBER = f"PN-{timestamp}-{unique_id}"
        PART_NAME = "Test Part Name"
        
        # Create part
        result = client.parts.create(
            number=PART_NUMBER,
            name=PART_NAME,
        )
        
        # Verify successful response
        assert_create_part_success(result)
        
        # Verify by searching
        list_result = client.parts.list(search_query=PART_NUMBER)
        assert_get_parts_success(list_result)
        
        found = False
        for part in list_result.data:
            if part.id == result.id:
                found = True
                assert part.number == PART_NUMBER
                assert part.name == PART_NAME
                # Should have one revision with default identifier "A"
                assert len(part.revisions) == 1
                assert part.revisions[0].number == "A"
                break
        
        assert found, f"Created part {result.id} not found in list"
    
    def test_create_part_default_revision(self, client: TofuPilot, auth_type: str) -> None:
        """Test that parts created without revision_number get default revision 'A'."""
            
        # Test constants - ensure uniqueness
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        PART_NUMBER = f"PN-DEFAULT-REV-{timestamp}-{unique_id}"
        PART_NAME = "Part with Default Revision"
        
        # Create part without specifying revision_number
        result = client.parts.create(
            number=PART_NUMBER,
            name=PART_NAME,
        )
        
        # Verify successful response
        assert_create_part_success(result)
        
        # Get the part and verify default revision
        list_result = client.parts.list(search_query=PART_NUMBER)
        assert_get_parts_success(list_result)
        
        found = False
        for part in list_result.data:
            if part.id == result.id:
                found = True
                assert part.number == PART_NUMBER
                assert part.name == PART_NAME
                # Should have exactly one revision with default identifier "A"
                assert len(part.revisions) == 1
                assert part.revisions[0].number == "A"
                assert part.revisions[0].unit_count == 0
                break
        
        assert found, f"Created part {result.id} not found in list"
    
    def test_create_part_with_revision(self, client: TofuPilot, auth_type: str) -> None:
        """Test creating a part with initial revision."""
            
        # Test constants - ensure uniqueness with uuid
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        PART_NUMBER = f"PN-REV-{timestamp}-{unique_id}"
        PART_NAME = "Part with Revision"
        REVISION_NUMBER = "REV-A"
        
        # Create part with revision
        result = client.parts.create(
            number=PART_NUMBER,
            name=PART_NAME,
            revision_number=REVISION_NUMBER,
        )
        
        # Verify successful response
        assert_create_part_success(result)
        
        # List and verify the revision was created
        list_result = client.parts.list(search_query=PART_NUMBER)
        assert_get_parts_success(list_result)
        
        found = False
        for part in list_result.data:
            if part.id == result.id:
                found = True
                assert part.number == PART_NUMBER
                assert part.name == PART_NAME
                # Should have one revision
                assert len(part.revisions) == 1
                assert part.revisions[0].number == REVISION_NUMBER
                assert part.revisions[0].unit_count == 0  # No units yet
                break
        
        assert found, f"Created part {result.id} not found in list"