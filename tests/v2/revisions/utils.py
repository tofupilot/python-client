"""Utility functions for revision tests."""

from tofupilot.v2.models.part_createrevisionop import PartCreateRevisionResponse
# Note: Revisions are listed through parts.list() endpoint, not a separate endpoint
from tofupilot.v2.models.part_getrevisionop import PartGetRevisionResponse
from tofupilot.v2.models.part_updaterevisionop import PartUpdateRevisionResponse
from tofupilot.v2.models.part_deleterevisionop import PartDeleteRevisionResponse


def assert_create_revision_success(result: PartCreateRevisionResponse) -> None:
    """Assert that revision create response is valid."""
    assert isinstance(result, PartCreateRevisionResponse)
    assert len(result.id) > 0


def assert_list_revisions_success(part_with_revisions) -> None:
    """Assert that part contains valid revisions."""
    assert hasattr(part_with_revisions, 'revisions')
    assert isinstance(part_with_revisions.revisions, list)
    
    for revision in part_with_revisions.revisions:
        assert len(revision.id) > 0
        assert hasattr(revision, 'number')
        assert hasattr(revision, 'unit_count') and revision.unit_count >= 0


def assert_get_revision_success(result: PartGetRevisionResponse) -> None:
    """Assert that revision get response is valid."""
    assert isinstance(result, PartGetRevisionResponse)
    assert len(result.id) > 0


def assert_update_revision_success(result: PartUpdateRevisionResponse) -> None:
    """Assert that revision update response is valid."""
    assert isinstance(result, PartUpdateRevisionResponse)
    assert len(result.id) > 0


def assert_delete_revision_success(result: PartDeleteRevisionResponse) -> None:
    """Assert that revision delete response is valid."""
    assert isinstance(result, PartDeleteRevisionResponse)
    assert len(result.id) > 0


# Removed get_revision_pagination_info - revisions are part of parts list, use part pagination