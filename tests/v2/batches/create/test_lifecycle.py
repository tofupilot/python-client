"""Test batch lifecycle including creation and direct unit association."""

from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_batch_success, assert_get_batches_success

class TestBatchLifecycle:

    def test_batch_with_units_association(self, client: TofuPilot, auth_type: str, procedure_id: str, timestamp) -> None:
        """Test creating a batch and associating it with units through run creation."""
        
        # Stations can create batches but cannot create runs with operated_by
        # We'll handle the station case later in the run creation section
        
        # Create batch
        batch_number = f"AutomatedTest-V2-Lifecycle-{timestamp}"
        batch_result = client.batches.create(number=batch_number)
        assert_create_batch_success(batch_result)
        
        # Create test data: part and revision for units
        part_number = f"BATCH-LIFECYCLE-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Batch Lifecycle {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create units with batch association through run creation
        unit_ids: list[str] = []
        for i in range(3):
            serial_number = f"UNIT-{i}-{timestamp}"
            
            # Create a run which will create the unit with the batch association
            if auth_type == "station":
                # Stations can create runs but without operated_by
                run_create_result = client.runs.create(
                    outcome="PASS",
                    procedure_id=procedure_id,
                    serial_number=serial_number,
                    part_number=part_number,
                    revision_number=revision_number,
                    batch_number=batch_number,
                    started_at=datetime.now(timezone.utc).isoformat(),
                    ended_at=datetime.now(timezone.utc).isoformat()
                )
            else:
                # Users can create runs with or without operated_by
                run_create_result = client.runs.create(
                    outcome="PASS",
                    procedure_id=procedure_id,
                    serial_number=serial_number,
                    part_number=part_number,
                    revision_number=revision_number,
                    batch_number=batch_number,
                    started_at=datetime.now(timezone.utc).isoformat(),
                    ended_at=datetime.now(timezone.utc).isoformat()
                )
            
            # Get the run details to retrieve the unit ID
            run_details = client.runs.get(id=run_create_result.id)
            unit_ids.append(run_details.unit.id)
        
        # Verify batch now has units
        batches_list = client.batches.list(ids=[batch_result.id])
        assert_get_batches_success(batches_list)
        assert len(batches_list.data) == 1
        
        batch_with_units = batches_list.data[0]
        assert batch_with_units.id == batch_result.id
        assert batch_with_units.number == batch_number
        assert hasattr(batch_with_units, 'units')
        assert len(batch_with_units.units) == 3
        
        # Verify unit details
        found_unit_ids = {unit.id for unit in batch_with_units.units}
        assert found_unit_ids == set(unit_ids)
        
        for unit in batch_with_units.units:
            assert unit.part is not None
            assert unit.part.number == part_number
            assert unit.part.revision.number == revision_number
    
    def test_batch_creation_and_immediate_listing(self, client: TofuPilot, timestamp) -> None:
        """Test that a newly created batch appears immediately in list results."""
        # Test constants
        BATCH_NUMBER = f"AutomatedTest-V2-Immediate-{timestamp}"
        
        # Create batch
        create_result = client.batches.create(number=BATCH_NUMBER)
        assert_create_batch_success(create_result)
        
        # Immediately list batches filtering by the created batch number
        list_result = client.batches.list(numbers=[BATCH_NUMBER])
        assert_get_batches_success(list_result)
        
        # Verify the batch is found
        assert len(list_result.data) == 1
        found_batch = list_result.data[0]
        assert found_batch.id == create_result.id
        assert found_batch.number == BATCH_NUMBER
        # created_at should be set
        assert hasattr(found_batch, 'created_at')
        assert found_batch.created_at is not None
        
        # Verify it also appears when filtering by ID
        list_by_id = client.batches.list(ids=[create_result.id])
        assert_get_batches_success(list_by_id)
        assert len(list_by_id.data) == 1
        assert list_by_id.data[0].id == create_result.id