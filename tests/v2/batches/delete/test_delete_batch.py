"""Test deleting batches."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_delete_batch_success
from ...utils import assert_station_access_forbidden


class TestDeleteBatch:
    """Test deleting batches."""

    def test_delete_batch(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test deleting a batch and verifying it's gone."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete batch"):
                client.batches.delete(number="any")
            return

        batch_number = f"DEL-BATCH-{timestamp}-{uuid.uuid4().hex[:8]}"
        client.batches.create(number=batch_number)

        result = client.batches.delete(number=batch_number)
        assert_delete_batch_success(result)

        with pytest.raises(ErrorNOTFOUND):
            client.batches.get(number=batch_number)

    def test_delete_nonexistent_batch(self, client: TofuPilot, auth_type: str) -> None:
        """Test deleting a batch that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("delete nonexistent batch"):
                client.batches.delete(number="nonexistent")
            return

        fake_number = f"NONEXISTENT-{uuid.uuid4().hex[:8]}"

        with pytest.raises(ErrorNOTFOUND):
            client.batches.delete(number=fake_number)
