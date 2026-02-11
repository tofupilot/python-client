"""Test updating batches."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND, ErrorCONFLICT
from ..utils import assert_update_batch_success, assert_get_batch_success
from ...utils import assert_station_access_forbidden


class TestUpdateBatch:
    """Test updating batches."""

    def test_update_batch_number(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating a batch's number."""
        if auth_type == "station":
            with assert_station_access_forbidden("update batch number"):
                client.batches.update(number="any", new_number="any-new")
            return

        batch_number = f"UPD-BATCH-{timestamp}-{uuid.uuid4().hex[:8]}"
        new_number = f"UPD-BATCH-NEW-{timestamp}-{uuid.uuid4().hex[:8]}"
        client.batches.create(number=batch_number)

        result = client.batches.update(number=batch_number, new_number=new_number)
        assert_update_batch_success(result)

        # Verify new number via get
        batch = client.batches.get(number=new_number)
        assert_get_batch_success(batch)
        assert batch.number == new_number

    def test_update_nonexistent_batch(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating a batch that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("update nonexistent batch"):
                client.batches.update(number="nonexistent", new_number="anything")
            return

        fake_number = f"NONEXISTENT-{uuid.uuid4().hex[:8]}"

        with pytest.raises(ErrorNOTFOUND):
            client.batches.update(number=fake_number, new_number="anything")

    def test_update_duplicate_number(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating to a number that already exists."""
        if auth_type == "station":
            with assert_station_access_forbidden("update duplicate batch number"):
                client.batches.update(number="any", new_number="any")
            return

        unique = uuid.uuid4().hex[:8]
        number_a = f"UPD-DUP-A-{timestamp}-{unique}"
        number_b = f"UPD-DUP-B-{timestamp}-{unique}"
        client.batches.create(number=number_a)
        client.batches.create(number=number_b)

        with pytest.raises(ErrorCONFLICT):
            client.batches.update(number=number_a, new_number=number_b)
