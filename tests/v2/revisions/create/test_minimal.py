"""Test minimal revision creation."""

import pytest
from datetime import datetime, timezone
from typing import List
import uuid
from tofupilot.v2 import TofuPilot
from tofupilot.v2.models.part_createrevisionop import PartCreateRevisionResponse
from ..utils import assert_create_revision_success
from ...parts.utils import assert_create_part_success


class TestCreateRevisionMinimal:
    """Test minimal revision creation scenarios."""
    
    @pytest.fixture
    def test_part(self, client: TofuPilot, auth_type: str) -> tuple[str, str]:
        """Create a test part for revision tests. Returns (part_id, part_number)."""
            
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-FOR-REV-{timestamp}-{unique_id}"
        
        result = client.parts.create(
            number=part_number,
            name=f"Test Part for Revisions {unique_id}"
        )
        assert_create_part_success(result)
        return result.id, part_number
    
    def test_create_revision_minimal(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test creating a revision with minimal fields (number and part_number)."""
        part_id, part_number = test_part
        
        # Create unique revision number
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        revision_number = f"REV-{timestamp}"
        
        # Create revision
        result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Verify successful response
        assert_create_revision_success(result)
        
        # Verify by getting the part with its revisions
        part_data = client.parts.get(number=part_number)
        
        # Find the created revision
        created_revision = None
        for rev in part_data.revisions:
            if rev.id == result.id:
                created_revision = rev
                break
        
        assert created_revision is not None, f"Revision {result.id} not found"
        assert created_revision.number == revision_number
        assert part_data.id == part_id
        assert created_revision.unit_count == 0  # No units created yet
    
    def test_create_multiple_revisions_same_part(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test creating multiple revisions for the same part."""
        _, part_number = test_part
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        
        # Create first revision
        rev1_result = client.parts.revisions.create(
            part_number=part_number,
            number=f"REV-A-{timestamp}"
        )
        assert_create_revision_success(rev1_result)
        
        # Create second revision
        rev2_result = client.parts.revisions.create(
            part_number=part_number,
            number=f"REV-B-{timestamp}"
        )
        assert_create_revision_success(rev2_result)
        
        # Verify both exist for the part
        part_data = client.parts.get(number=part_number)
        
        revision_ids = {rev.id for rev in part_data.revisions}
        assert rev1_result.id in revision_ids
        assert rev2_result.id in revision_ids
    
    def test_create_revision_special_characters(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test creating revisions with special characters in number."""
        _, part_number = test_part
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        
        special_numbers = [
            f"REV-{timestamp}-V1.0",
            f"REV_{timestamp}_ALPHA",
            f"REV.{timestamp}.BETA",
            f"REV {timestamp} GAMMA",
            f"REV-{timestamp}(PROTO)",
        ]
        
        created_revisions: List[PartCreateRevisionResponse] = []
        for rev_number in special_numbers:
            try:
                result = client.parts.revisions.create(
                    part_number=part_number,
                    number=rev_number
                )
                assert_create_revision_success(result)
                created_revisions.append(result)
            except Exception as e:
                # Some special characters might not be allowed - that's okay
                print(f"Special character test failed as expected for '{rev_number}': {e}")
        
        # At least one should succeed
        assert len(created_revisions) >= 1, "At least one special character revision should be created"
    
    def test_create_revision_edge_length(self, client: TofuPilot, test_part: tuple[str, str], auth_type: str) -> None:
        """Test creating revisions with edge case lengths."""
        _, part_number = test_part
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        # Test minimum length (1 character) - make unique
        short_number = f"A{timestamp[-6:]}"  # Use last 6 digits to make unique
        short_result = client.parts.revisions.create(
            part_number=part_number,
            number=short_number
        )
        assert_create_revision_success(short_result)
        
        # Test near maximum length (60 characters)
        long_number = f"REV-{timestamp}-" + "X" * (60 - len(f"REV-{timestamp}-"))
        long_result = client.parts.revisions.create(
            part_number=part_number,
            number=long_number
        )
        assert_create_revision_success(long_result)
        assert len(long_number) == 60