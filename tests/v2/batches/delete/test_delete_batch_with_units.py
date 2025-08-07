"""Test deleting batches that have associated units."""

from datetime import datetime, timezone
from typing import List
from tofupilot.v2 import TofuPilot
from ..utils import assert_create_batch_success, assert_get_batches_success, assert_delete_batch_success
from ...utils import assert_station_access_forbidden


class TestDeleteBatchWithUnits:
    
    def test_delete_batch_with_units_succeeds(self, client: TofuPilot, auth_type: str, procedure_id: str, timestamp) -> None:
        """Test that deleting a batch with units succeeds and disassociates units."""
        
        # Create a batch
        batch_number = f"AutomatedTest-V2-Delete-WithUnits-{timestamp}"
        batch_result = client.batches.create(number=batch_number)
        assert_create_batch_success(batch_result)
        
        # Create test data: part and revision for unit
        part_number = f"DELETE-WITH-UNITS-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Delete With Units {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create a unit associated with this batch through run creation
        serial_number = f"UNIT-{timestamp}"
        
        if auth_type == "station":
            # Stations can create runs which will create units with batch association
            run_result = client.runs.create(
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
            # Users can also create runs
            run_result = client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number=serial_number,
                part_number=part_number,
                revision_number=revision_number,
                batch_number=batch_number,
                started_at=datetime.now(timezone.utc).isoformat(),
                ended_at=datetime.now(timezone.utc).isoformat()
            )
        
        if auth_type == "user":
            # Users can delete batches with units (units will be disassociated)
            delete_result = client.batches.delete(number=batch_number)
            assert_delete_batch_success(delete_result)
            
            # Verify batch is gone
            list_result = client.batches.list(ids=[batch_result.id])
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 0
            
            # Verify unit still exists but is no longer associated with batch
            unit_list = client.units.list(serial_numbers=[serial_number])
            assert len(unit_list.data) == 1
            # Check if batch property exists and is None (unit is disassociated from batch)
            unit = unit_list.data[0]
            assert not hasattr(unit, 'batch') or unit.batch is None
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete batch with units"):
                client.batches.delete(number=batch_number)
    
    def test_delete_batch_with_multiple_units_succeeds(self, client: TofuPilot, auth_type: str, procedure_id: str, timestamp) -> None:
        """Test that deleting a batch with multiple units succeeds and disassociates units."""
        
        # Create a batch
        batch_number = f"AutomatedTest-V2-Delete-MultiUnits-{timestamp}"
        batch_result = client.batches.create(number=batch_number)
        assert_create_batch_success(batch_result)
        
        # Create test data: part and revision for units
        part_number = f"DELETE-MULTI-UNITS-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Delete Multi Units {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create multiple units associated with this batch through run creation
        unit_serials: List[str] = []
        for i in range(3):
            serial_number = f"UNIT-{i}-{timestamp}"
            
            if auth_type == "station":
                # Stations can create runs which will create units with batch association
                run_result = client.runs.create(
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
                # Users can also create runs
                run_result = client.runs.create(
                    outcome="PASS",
                    procedure_id=procedure_id,
                    serial_number=serial_number,
                    part_number=part_number,
                    revision_number=revision_number,
                    batch_number=batch_number,
                    started_at=datetime.now(timezone.utc).isoformat(),
                    ended_at=datetime.now(timezone.utc).isoformat()
                )
            unit_serials.append(serial_number)
        
        if auth_type == "user":
            # Users can delete batches with units (units will be disassociated)
            delete_result = client.batches.delete(number=batch_number)
            assert_delete_batch_success(delete_result)
            
            # Verify batch is gone
            list_result = client.batches.list(ids=[batch_result.id])
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 0
            
            # Verify all units still exist but are no longer associated with batch
            unit_list = client.units.list(serial_numbers=unit_serials)
            assert len(unit_list.data) == 3
            for unit in unit_list.data:
                # Check if batch property exists and is None (unit is disassociated from batch)
                assert not hasattr(unit, 'batch') or unit.batch is None
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete batch with multiple units"):
                client.batches.delete(number=batch_number)
    
    def test_batch_deletion_with_unit_lifecycle(self, client: TofuPilot, auth_type: str, procedure_id: str, timestamp) -> None:
        """Test batch deletion behavior in a complete unit lifecycle scenario."""
        
        # Create a batch
        batch_number = f"AutomatedTest-V2-Delete-Lifecycle-{timestamp}"
        batch_result = client.batches.create(number=batch_number)
        assert_create_batch_success(batch_result)
        
        # Create test data: part and revision for unit
        part_number = f"DELETE-LIFECYCLE-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Delete Lifecycle {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create a unit with this batch through run creation
        serial_number = f"UNIT-TEMP-{timestamp}"
        
        if auth_type == "station":
            # Stations can create runs which will create units with batch association
            run_result = client.runs.create(
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
            # Users can also create runs
            run_result = client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number=serial_number,
                part_number=part_number,
                revision_number=revision_number,
                batch_number=batch_number,
                started_at=datetime.now(timezone.utc).isoformat(),
                ended_at=datetime.now(timezone.utc).isoformat()
            )
        
        if auth_type == "user":
            # Batch deletion should succeed even with units (units will be disassociated)
            delete_result = client.batches.delete(number=batch_number)
            assert_delete_batch_success(delete_result)
            
            # Verify unit still exists but no longer has batch association
            unit_list = client.units.list(serial_numbers=[serial_number])
            assert len(unit_list.data) == 1
            unit = unit_list.data[0]
            # Check if batch property exists and is None (unit is disassociated from batch)
            assert not hasattr(unit, 'batch') or unit.batch is None
            unit_id = unit.id
            
            # Clean up: delete the unit (users can delete units)
            client.units.delete(serial_numbers=[serial_number])
            
            # Verify batch is gone
            list_result = client.batches.list(ids=[batch_result.id])
            assert_get_batches_success(list_result)
            assert len(list_result.data) == 0
        else:
            # Stations cannot delete batches (HTTP 403 FORBIDDEN)
            with assert_station_access_forbidden("delete batch in lifecycle scenario"):
                client.batches.delete(number=batch_number)