"""Test getting individual batch details."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_get_batch_success


class TestGetBatch:
    """Test getting individual batch details."""

    def test_get_batch_by_number(self, client: TofuPilot, timestamp) -> None:
        """Test getting a batch by number and verifying fields."""
        batch_number = f"GET-BATCH-{timestamp}-{uuid.uuid4().hex[:8]}"
        create_result = client.batches.create(number=batch_number)

        result = client.batches.get(number=batch_number)
        assert_get_batch_success(result)

        assert result.id == create_result.id
        assert result.number == batch_number
        assert result.created_at is not None
        assert result.units is not None

    def test_get_nonexistent_batch(self, client: TofuPilot) -> None:
        """Test getting a batch that doesn't exist."""
        fake_number = f"NONEXISTENT-{uuid.uuid4().hex[:8]}"

        with pytest.raises(ErrorNOTFOUND):
            client.batches.get(number=fake_number)
