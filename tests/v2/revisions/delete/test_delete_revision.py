"""Test revision deletion functionality."""

from datetime import datetime, timezone
import pytest
import uuid
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_revision_success, assert_delete_revision_success
from ...parts.utils import assert_create_part_success, assert_get_parts_success
from ...utils import assert_station_access_limited


class TestDeleteRevision:
    """Test revision deletion scenarios."""
    
    @pytest.fixture
    def test_part(self, client: TofuPilot, auth_type: str, timestamp: str) -> tuple[str, str]:
        """Create a test part for revision deletion tests."""
            
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-DEL-{timestamp}-{unique_id}"
        
        result = client.parts.create(
            number=part_number,
            name=f"Delete Test Part {unique_id}"
        )
        assert_create_part_success(result)
        return result.id, part_number
    
    @pytest.fixture
    def test_revision(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str, timestamp: str) -> tuple[str, str]:
        """Create a test revision for deletion tests."""
            
        _, part_number = test_part
        revision_number = f"REV-DELETE-{timestamp}"
        result = client.parts.revisions.create(part_number=part_number
        , number=revision_number)
        assert_create_revision_success(result)
        return result.id, revision_number
    
    def test_delete_revision_success(self, client: TofuPilot, test_revision: tuple[str, str], test_part: tuple[str, str], auth_type: str) -> None:
        """Test successful revision deletion."""
        revision_id, revision_number = test_revision
        _, part_number = test_part
            
        # Verify revision exists before deletion
        part_before = client.parts.get(number=part_number)
        revision_exists = any(rev.id == revision_id for rev in part_before.revisions)
        assert revision_exists, f"Revision {revision_id} should exist before deletion"
        
        # Behavior differs by auth type:
        # - Station auth: cannot delete revisions (403 Forbidden)
        # - User auth: hard deletion (revision removed from list)
        if auth_type == "station":
            # Station has limited access - cannot delete revisions at all
            from tofupilot.v2.errors import APIError
            with pytest.raises(APIError) as exc_info:
                client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
            assert "403" in str(exc_info.value) or "cannot delete revisions" in str(exc_info.value).lower()
        else:  # user auth
            # Delete the revision
            result = client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
            assert_delete_revision_success(result)
            assert result.id == revision_id
            
            # Verify revision was removed (hard delete)
            part_after = client.parts.get(number=part_number)
            revision_still_exists = any(rev.id == revision_id for rev in part_after.revisions)
            assert not revision_still_exists  # Removed from list (hard delete)
    
    def test_delete_revision_doesnt_affect_part(self, client: TofuPilot, test_revision: tuple[str, str], test_part: tuple[str, str], auth_type: str, timestamp) -> None:
        """Test that deleting revision doesn't affect the part."""
        revision_id, revision_number = test_revision
        part_id, part_number = test_part
        
        # Stations cannot delete revisions - should get 403 Forbidden
        if auth_type == "station":
            from ...utils import assert_station_access_forbidden
            with assert_station_access_forbidden("delete revision"):
                client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
            return
        
        # Create a second revision for the same part before testing
        second_revision = client.parts.revisions.create(part_number=part_number
        , number=f"REV-SECOND-{timestamp}")
        assert_create_revision_success(second_revision)
        
        # Get the part to verify the revision exists before deleting it
        part_data = client.parts.get(number=part_number)
        assert part_data.id == part_id
        revision_exists = any(rev.id == revision_id for rev in part_data.revisions)
        assert revision_exists, f"Revision {revision_id} should exist before deletion"
            
        # Delete the revision
        result = client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
        assert_delete_revision_success(result)
        
        # Verify part still exists by creating a new revision for it
        new_revision_result = client.parts.revisions.create(part_number=part_number
        , number=f"REV-AFTER-DELETE-{timestamp}")
        assert_create_revision_success(new_revision_result)
        
        # Verify the second revision still exists
        part_after = client.parts.get(number=part_number)
        second_rev_exists = any(rev.id == second_revision.id for rev in part_after.revisions)
        assert second_rev_exists, f"Second revision {second_revision.id} should still exist"
        assert part_after.id == part_id
    
    def test_delete_nonexistent_revision_fails(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test deleting non-existent revision fails."""
        _, part_number = test_part
        fake_revision_number = "REV-NONEXISTENT-00000000"
        
        if auth_type == "station":
            # Stations cannot delete revisions at all (403 Forbidden)
            from tofupilot.v2.errors import APIError
            with pytest.raises(APIError) as exc_info:
                client.parts.revisions.delete(part_number=part_number, revision_number=fake_revision_number)
            assert "403" in str(exc_info.value) or "cannot delete revisions" in str(exc_info.value).lower()
        else:
            # Users get 404 for non-existent revision
            with pytest.raises(ErrorNOTFOUND) as exc_info:
                client.parts.revisions.delete(part_number=part_number, revision_number=fake_revision_number)
            
            # Verify the error is about revision not found
            error_message = str(exc_info.value).lower()
            assert "not found" in error_message
    
    def test_delete_one_of_multiple_revisions(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str, timestamp: str) -> None:
        """Test deleting one revision when multiple exist for the same part."""
        
        # Stations cannot delete revisions - should get 403 Forbidden
        if auth_type == "station":
            from ...utils import assert_station_access_forbidden
            _, part_number = test_part
            # Create a test revision to attempt deletion
            revision_number = f"REV-MULTI-{timestamp}"
            with assert_station_access_forbidden("delete revision"):
                client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
            return
            
        _, part_number = test_part
        
        # Create multiple revisions for the same part
        rev1_result = client.parts.revisions.create(part_number=part_number
        , number=f"REV-MULTI-1-{timestamp}")
        assert_create_revision_success(rev1_result)
        
        rev2_result = client.parts.revisions.create(part_number=part_number
        , number=f"REV-MULTI-2-{timestamp}")
        assert_create_revision_success(rev2_result)
        
        rev3_result = client.parts.revisions.create(part_number=part_number
        , number=f"REV-MULTI-3-{timestamp}")
        assert_create_revision_success(rev3_result)
        
        # Verify all 3 exist
        part_before = client.parts.get(number=part_number)
        revision_ids_before = {rev.id for rev in part_before.revisions}
        assert rev1_result.id in revision_ids_before
        assert rev2_result.id in revision_ids_before
        assert rev3_result.id in revision_ids_before
        
        # Delete the middle revision
        delete_result = client.parts.revisions.delete(part_number=part_number, revision_number=f"REV-MULTI-2-{timestamp}")
        assert_delete_revision_success(delete_result)
        
        # For user auth: hard deletion (deleted revision removed)
        part_after = client.parts.get(number=part_number)
        revision_ids_after = {rev.id for rev in part_after.revisions}
        
        assert rev1_result.id in revision_ids_after  # Still exists
        assert rev3_result.id in revision_ids_after  # Still exists
        assert rev2_result.id not in revision_ids_after  # Removed (hard delete)
    
    def test_delete_revision_twice_behavior(self, client: TofuPilot, test_revision: tuple[str, str], test_part: tuple[str, str], auth_type: str) -> None:
        """Test deleting the same revision twice."""
        revision_id, revision_number = test_revision
        _, part_number = test_part
        
        # Stations cannot delete revisions - should get 403 Forbidden
        if auth_type == "station":
            from ...utils import assert_station_access_forbidden
            with assert_station_access_forbidden("delete revision"):
                client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
            return
            
        # Delete the revision first time
        result1 = client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
        assert_delete_revision_success(result1)
        
        # For user auth: second delete fails with 404
        with pytest.raises(ErrorNOTFOUND) as exc_info:
            client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
        
        error_message = str(exc_info.value).lower()
        assert "not found" in error_message
    
    def test_delete_revision_with_malformed_uuid_fails(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting revision with malformed part number fails."""
        
        if auth_type == "station":
            # Stations cannot delete revisions at all (403 Forbidden)
            from tofupilot.v2.errors import APIError
            with pytest.raises(APIError) as exc_info:
                client.parts.revisions.delete(part_number="not-a-valid-part", revision_number="REV-001")
            assert "403" in str(exc_info.value) or "cannot delete revisions" in str(exc_info.value).lower()
        else:
            with pytest.raises(Exception) as exc_info:
                client.parts.revisions.delete(part_number="not-a-valid-part", revision_number="REV-001")
            
            # Should get some kind of validation error
            error_message = str(exc_info.value).lower()
            assert "not found" in error_message or "invalid" in error_message or "bad" in error_message
    
    def test_delete_last_revision_deletes_part(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test that deleting the last revision of a part also deletes the part (orphan deletion)."""
        
        # Stations cannot delete revisions - should get 403 Forbidden
        if auth_type == "station":
            from ...utils import assert_station_access_forbidden
            # Create a test part to attempt revision deletion
            unique_id = str(uuid.uuid4())[:8]
            part_number = f"PART-ORPHAN-{timestamp}-{unique_id}"
            revision_number = f"REV-ORPHAN-{timestamp}"
            with assert_station_access_forbidden("delete revision"):
                client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
            return
        
        # Create a part with a single revision
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-ORPHAN-{timestamp}-{unique_id}"
        
        # Create part (which now automatically creates a default revision)
        part_result = client.parts.create(
            number=part_number,
            name=f"Orphan Test Part {unique_id}"
        )
        assert_create_part_success(part_result)
        part_id = part_result.id
        
        # Get the part to find the default revision
        parts_list = client.parts.list(search_query=part_number)
        assert_get_parts_success(parts_list)
        assert len(parts_list.data) == 1
        part = parts_list.data[0]
        assert part.id == part_id
        assert len(part.revisions) == 1  # Should have exactly one revision
        revision_id = part.revisions[0].id
        revision_number = part.revisions[0].number
        
        # Verify the part exists before deletion
        parts_before = client.parts.list(search_query=part_number)
        assert_get_parts_success(parts_before)
        assert len(parts_before.data) == 1
        assert parts_before.data[0].id == part_id
        
        # Delete the only revision (only users can do this)
        delete_result = client.parts.revisions.delete(part_number=part_number, revision_number=revision_number)
        assert_delete_revision_success(delete_result)
        assert delete_result.id == revision_id
        
        # Verify the part has been deleted (orphan deletion)
        parts_after = client.parts.list(search_query=part_number)
        assert_get_parts_success(parts_after)
        
        # The part should be deleted due to orphan cascade
        assert len(parts_after.data) == 0, "Part should be deleted when its last revision is deleted"
        
        # Also verify by part number search
        parts_by_number = client.parts.list(search_query=part_number)
        assert_get_parts_success(parts_by_number)
        assert len(parts_by_number.data) == 0, "Part should not be found by part number after orphan deletion"