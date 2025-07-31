"""Test batch GET endpoint."""

import pytest
import time
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_batch_success


class TestGetBatch:
    """Test retrieving individual batches by number."""

    def test_get_existing_batch(self, client: TofuPilot):
        """Test retrieving an existing batch by its number."""
        # Create a batch with unique number
        timestamp = str(int(time.time() * 1000000))  # microsecond timestamp
        batch_number = f"TEST-BATCH-{timestamp}"
        create_response = client.batches.create(number=batch_number)
        assert_create_batch_success(create_response)
        
        # Get the batch by number
        batch = client.batches.get(number=batch_number)
        
        # Verify response
        assert batch.id == create_response.id
        assert batch.number == batch_number
        assert batch.created_at is not None
        assert hasattr(batch, 'units')
        assert batch.units == []  # New batch has no units

    def test_get_batch_with_units(self, client: TofuPilot, procedure_id: str):
        """Test retrieving a batch that has units."""
        from datetime import datetime, timezone
        
        # Create batch with unique number
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        batch_number = f"TEST-BATCH-WITH-UNITS-{timestamp}"
        batch_response = client.batches.create(number=batch_number)
        assert_create_batch_success(batch_response)
        
        # Create test data: part and revision for units
        part_number = f"GET-BATCH-UNITS-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Get Batch With Units {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create units through run creation with batch association
        unit_serials = [f"UNIT-{timestamp}-{i:03d}" for i in range(3)]
        for serial in unit_serials:
            # Create a run which will create the unit with the batch association
            client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number=serial,
                part_number=part_number,
                revision_number=revision_number,
                batch_number=batch_number,
                started_at=datetime.now(timezone.utc).isoformat(),
                ended_at=datetime.now(timezone.utc).isoformat()
            )
        
        # Get the batch
        batch = client.batches.get(number=batch_number)
        
        # Verify batch has units
        assert batch.units is not None
        assert len(batch.units) == 3
        unit_serial_numbers = [unit.serial_number for unit in batch.units]
        assert set(unit_serial_numbers) == set(unit_serials)
        
        # Verify unit details
        for unit in batch.units:
            assert unit.id is not None
            assert unit.serial_number in unit_serials
            assert unit.part is not None
            assert unit.part.number == part_number
            assert unit.part.revision.number == revision_number

    def test_get_nonexistent_batch(self, client: TofuPilot):
        """Test retrieving a non-existent batch returns 404."""
        with pytest.raises(ErrorNOTFOUND):
            client.batches.get(number="NONEXISTENT-BATCH-999")

    def test_get_batch_created_by_user(self, client: TofuPilot, auth_type: str):
        """Test batch includes creator information."""
        # Create batch with unique number
        timestamp = str(int(time.time() * 1000000))
        batch_number = f"TEST-BATCH-USER-{timestamp}"
        batch_response = client.batches.create(number=batch_number)
        assert_create_batch_success(batch_response)
        
        # Get the batch
        batch = client.batches.get(number=batch_number)
        
        # Verify creator info based on auth type
        from tofupilot.v2.types import UNSET
        if auth_type == 'user':
            # User-created batch should have created_by_user
            assert batch.created_by_user not in (UNSET, None)
            if hasattr(batch, 'created_by_user') and batch.created_by_user:
                if hasattr(batch.created_by_user, 'id'):
                    assert batch.created_by_user.id is not None
            # Should not have created_by_station
            assert batch.created_by_station in (UNSET, None)
        else:
            # Station-created batch should have created_by_station
            assert batch.created_by_station not in (UNSET, None)
            if hasattr(batch, 'created_by_station') and batch.created_by_station:
                if hasattr(batch.created_by_station, 'id'):
                    assert batch.created_by_station.id is not None
            # Should not have created_by_user
            assert batch.created_by_user in (UNSET, None)