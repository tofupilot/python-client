"""Utility functions for batch tests."""

from trycast import checkcast

from tofupilot.v2.models.batch_createop import BatchCreateResponse
from tofupilot.v2.models.batch_listop import BatchListResponse
from tofupilot.v2.models.batch_deleteop import BatchDeleteResponse


def assert_create_batch_success(result: BatchCreateResponse) -> None:
    """Assert that batch create response is valid."""
    assert checkcast(BatchCreateResponse, result)
    assert len(result.id) > 0


def assert_get_batches_success(result: BatchListResponse) -> None:
    """Assert that batch list response is valid."""
    assert checkcast(BatchListResponse, result)
    for batch in result.data:
        assert len(batch.id) > 0


def assert_delete_batch_success(result: BatchDeleteResponse) -> None:
    """Assert that batch delete response is valid."""
    assert checkcast(BatchDeleteResponse, result)
    assert len(result.id) > 0