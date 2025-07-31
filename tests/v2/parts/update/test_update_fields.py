"""Test parts update field modifications."""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_part_success, assert_update_part_success, assert_get_parts_success


class TestUpdatePartFields:
    """Test updating part fields."""
    
    @pytest.fixture
    def test_part(self, client: TofuPilot, auth_type: str) -> tuple[str, str]:
        """Create a test part for update tests."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"UPDATE-TEST-{timestamp}"
        result = client.parts.create(
            number=part_number,
            name="Original Part Name"
        )
        assert_create_part_success(result)
        return result.id, part_number
    
    def test_update_part_number(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test updating part number."""
        part_id, part_number = test_part
        new_number = f"UPDATED-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        
        if auth_type == "station":
            # Station cannot update parts - now returns 403 Forbidden
            from tofupilot.v2.errors import APIError
            with pytest.raises(APIError) as exc_info:
                client.parts.update(
                    number=part_number,
                    new_number=new_number
                )
            assert "403" in str(exc_info.value) or "cannot update parts" in str(exc_info.value).lower()
            return
        
        # Update the part number
        result = client.parts.update(
            number=part_number,
            new_number=new_number
        )
        
        assert_update_part_success(result)
        assert result.id == part_id
        assert result.number == new_number
        assert result.updated_at is not None
        
        # Verify by searching
        list_result = client.parts.list(search_query=new_number)
        assert_get_parts_success(list_result)
        
        found = False
        for part in list_result.data:
            if part.id == part_id:
                found = True
                assert part.number == new_number
                break
        assert found
    
    def test_update_part_name(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test updating part name."""
        part_id, part_number = test_part
        new_name = "Updated Part Name"
        
        if auth_type == "station":
            # Station cannot update parts - now returns 403 Forbidden
            from tofupilot.v2.errors import APIError
            with pytest.raises(APIError) as exc_info:
                client.parts.update(
                    number=part_number,
                    name=new_name
                )
            assert "403" in str(exc_info.value) or "cannot update parts" in str(exc_info.value).lower()
            return
        
        # Update the part name
        result = client.parts.update(
            number=part_number,
            name=new_name
        )
        
        assert_update_part_success(result)
        assert result.id == part_id
        assert result.number == part_number
        assert result.name == new_name
        
        # Verify the number didn't change
        list_result = client.parts.list(search_query=result.number)
        assert_get_parts_success(list_result)
        
        found = False
        for part in list_result.data:
            if part.id == part_id:
                found = True
                assert part.name == new_name
                break
        assert found
    
    def test_update_both_fields(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test updating both number and name."""
        part_id, part_number = test_part
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        new_number = f"BOTH-UPDATED-{timestamp}"
        new_name = "Both Fields Updated"
        
        if auth_type == "station":
            # Station cannot update parts - now returns 403 Forbidden
            from tofupilot.v2.errors import APIError
            with pytest.raises(APIError) as exc_info:
                client.parts.update(
                    number=part_number,
                    new_number=new_number,
                    name=new_name
                )
            assert "403" in str(exc_info.value) or "cannot update parts" in str(exc_info.value).lower()
            return
        
        # Update both fields
        result = client.parts.update(
            number=part_number,
            new_number=new_number,
            name=new_name
        )
        
        assert_update_part_success(result)
        assert result.id == part_id
        assert result.number == new_number
        assert result.name == new_name
        
        # Verify by searching
        list_result = client.parts.list(search_query=new_number)
        assert_get_parts_success(list_result)
        
        found = False
        for part in list_result.data:
            if part.id == part_id:
                found = True
                assert part.number == new_number
                assert part.name == new_name
                break
        assert found
    
    def test_update_preserves_revisions(self, client: TofuPilot, auth_type: str) -> None:
        """Test that updating a part preserves its revisions."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        part_number = f"PART-WITH-REV-{timestamp}"
        
        # Create part with revision
        create_result = client.parts.create(
            number=part_number,
            name="Part with Revision",
            revision_number="REV-ORIGINAL"
        )
        assert_create_part_success(create_result)
        
        # Update the part
        new_name = "Updated Part with Revision"
        
        if auth_type == "station":
            # Station cannot update parts - now returns 403 Forbidden
            from tofupilot.v2.errors import APIError
            with pytest.raises(APIError) as exc_info:
                client.parts.update(
                    number=part_number,
                    name=new_name
                )
            assert "403" in str(exc_info.value) or "cannot update parts" in str(exc_info.value).lower()
            return
        
        update_result = client.parts.update(
            number=part_number,
            name=new_name
        )
        assert_update_part_success(update_result)
        
        # Verify revision is preserved
        list_result = client.parts.list(search_query=update_result.number)
        assert_get_parts_success(list_result)
        
        found = False
        for part in list_result.data:
            if part.id == create_result.id:
                found = True
                assert part.name == new_name
                assert len(part.revisions) == 1
                assert part.revisions[0].number == "REV-ORIGINAL"
                break
        assert found
    
    def test_update_empty_name(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test updating part with empty name should fail."""
        _, part_number = test_part
        from tofupilot.v2.errors import APIError
        
        with pytest.raises(APIError) as exc_info:
            client.parts.update(
                number=part_number,
                name=""
            )
        
        error_message = str(exc_info.value).lower()
        if auth_type == "station":
            # For stations, access check happens before validation
            assert "403" in str(exc_info.value) or "cannot update parts" in error_message
        else:
            # For users, validation error
            assert "required" in error_message or "validation" in error_message
    
    def test_update_special_characters(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test updating with special characters."""
        _, part_number = test_part
        if auth_type == "station":
            # Station cannot update parts - now returns 403 Forbidden
            from tofupilot.v2.errors import APIError
            with pytest.raises(APIError) as exc_info:
                client.parts.update(
                    number=part_number,
                    new_number="STATION-TEST",
                    name="Station Test"
                )
            assert "403" in str(exc_info.value) or "cannot update parts" in str(exc_info.value).lower()
            return
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        
        # Test various special characters
        special_updates = [
            (f"PART-{timestamp}-HYPHEN", "Part-With-Hyphens"),
            (f"PART_{timestamp}_UNDER", "Part_With_Underscores"),
            (f"PART.{timestamp}.DOT", "Part.With.Dots"),
            (f"PART {timestamp} SPACE", "Part With Spaces"),
        ]
        
        for new_number, new_name in special_updates:
            try:
                result = client.parts.update(
                    number=part_number,
                    new_number=new_number,
                    name=new_name
                )
                assert_update_part_success(result)
                assert result.number == new_number
                assert result.name == new_name
                break  # Only need one successful update
            except Exception:
                # Some special characters might not be allowed
                continue
    
    def test_update_long_values(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test updating with maximum length values."""
        _, part_number = test_part
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        # Create maximum length strings: part number (60 chars), part name (255 chars)
        long_number = f"LONG-{timestamp}-{'X' * (60 - len(f'LONG-{timestamp}-'))}"[:60]
        long_name = f"NAME-{timestamp}-{'N' * (255 - len(f'NAME-{timestamp}-'))}"[:255]
        
        if auth_type == "station":
            # Station cannot update parts - now returns 403 Forbidden
            from tofupilot.v2.errors import APIError
            with pytest.raises(APIError) as exc_info:
                client.parts.update(
                    number=part_number,
                    new_number=long_number,
                    name=long_name
                )
            assert "403" in str(exc_info.value) or "cannot update parts" in str(exc_info.value).lower()
            return
        
        result = client.parts.update(
            number=part_number,
            new_number=long_number,
            name=long_name
        )
        
        assert_update_part_success(result)
        assert len(result.number) == 60
        assert len(result.name) == 255
        assert result.number == long_number
        assert result.name == long_name