"""Utility functions for parts tests."""

from trycast import checkcast

from tofupilot.v2.models.part_createop import PartCreateResponse
from tofupilot.v2.models.part_listop import PartListResponse
from tofupilot.v2.models.part_updateop import PartUpdateResponse


def assert_create_part_success(result: PartCreateResponse) -> None:
    """Assert that part create response is valid."""
    assert checkcast(PartCreateResponse, result)
    assert len(result.id) > 0


def assert_get_parts_success(result: PartListResponse) -> None:
    """Assert that part list response is valid."""
    assert checkcast(PartListResponse, result)


def assert_update_part_success(result: PartUpdateResponse) -> None:
    """Assert that part update response is valid."""
    assert checkcast(PartUpdateResponse, result)