"""Test unit deletion functionality."""

import pytest
from datetime import datetime, timezone
from typing import List
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ...utils import assert_delete_units_success, assert_station_access_limited


class TestDeleteUnits:

    def test_delete_single_unit(self, client: TofuPilot, auth_type: str, timestamp: str):
        """Test deleting a single unit."""
        if auth_type == "station":
            # Stations have limited access to delete units
            fake_serial_number = "FAKE-UNIT-001"
            with assert_station_access_limited("delete single unit"):
                client.units.delete(serial_numbers=[fake_serial_number])
            return
            
        # Create test data: part, revision, and unit
        part_number = f"DELETE-SINGLE-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Delete Single {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create unit to delete
        serial_number = f"UNIT-DELETE-{timestamp}"
        unit_result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number
        )
        unit_id = unit_result.id
        
        # Users can delete units
        result = client.units.delete(serial_numbers=[serial_number])
        assert_delete_units_success(result)

        # Extract the actual list of deleted IDs from the response
        assert unit_id in result.ids
        assert len(result.ids) == 1

    def test_delete_multiple_units(self, client: TofuPilot, auth_type: str, timestamp: str):
        """Test deleting multiple units."""
        if auth_type == "station":
            # Stations have limited access to delete units
            fake_serial_numbers = ["FAKE-UNIT-001", "FAKE-UNIT-002"]
            with assert_station_access_limited("delete multiple units"):
                client.units.delete(serial_numbers=fake_serial_numbers)
            return
            
        # Create test data: part, revision, and multiple units
        part_number = f"DELETE-MULTI-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Delete Multiple {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create multiple units to delete
        unit_ids: List[str] = []
        serial_numbers: List[str] = []
        for i in range(2):
            serial_number = f"UNIT-DELETE-{i}-{timestamp}"
            unit_result = client.units.create(
                serial_number=serial_number,
                part_number=part_number,
                revision_number=revision_number
            )
            unit_ids.append(unit_result.id)
            serial_numbers.append(serial_number)
        
        # Users can delete units
        result = client.units.delete(serial_numbers=serial_numbers)
        assert_delete_units_success(result)

        # Extract the actual list of deleted IDs from the response
        deleted_ids = result.ids
        for unit_id in unit_ids:
            assert unit_id in deleted_ids
        
        assert len(deleted_ids) == len(unit_ids)

    def test_delete_nonexistent_unit(self, client: TofuPilot, auth_type: str):
        """Test deleting a unit that doesn't exist."""
        fake_serial_number = "NONEXISTENT-UNIT-000"
        
        if auth_type == "user":
            # Users get proper error for non-existent units
            with pytest.raises(ErrorNOTFOUND):
                client.units.delete(serial_numbers=[fake_serial_number])
        else:
            # Stations have limited access to delete units
            with assert_station_access_limited("delete nonexistent unit"):
                client.units.delete(serial_numbers=[fake_serial_number])

    def test_delete_response_structure(self, client: TofuPilot, auth_type: str, timestamp: str):
        """Test the structure of delete response."""
        if auth_type == "station":
            # Stations have limited access to delete units
            fake_serial_number = "FAKE-UNIT-003"
            with assert_station_access_limited("delete unit for response structure test"):
                client.units.delete(serial_numbers=[fake_serial_number])
            return
            
        # Create test data: part, revision, and unit
        part_number = f"DELETE-RESPONSE-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Delete Response {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create unit to delete
        serial_number = f"UNIT-DELETE-{timestamp}"
        unit_result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number
        )
        unit_id = unit_result.id
        
        # Users can delete units
        result = client.units.delete(serial_numbers=[serial_number])
        
        # Test the response structure
        deleted_ids = result.ids
        assert isinstance(deleted_ids, list)
        assert unit_id in deleted_ids

    def test_delete_batch_units(self, client: TofuPilot, auth_type: str, timestamp: str):
        """Test deleting multiple units in batch."""
        if auth_type == "station":
            # Stations have limited access to delete units
            fake_serial_numbers = ["FAKE-UNIT-004", "FAKE-UNIT-005", "FAKE-UNIT-006"]
            with assert_station_access_limited("delete batch units"):
                client.units.delete(serial_numbers=fake_serial_numbers)
            return
            
        # Create test data: part, revision, and multiple units
        part_number = f"DELETE-BATCH-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Delete Batch {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create multiple units to delete
        unit_ids: List[str] = []
        serial_numbers: List[str] = []
        for i in range(3):
            serial_number = f"UNIT-BATCH-DELETE-{i}-{timestamp}"
            unit_result = client.units.create(
                serial_number=serial_number,
                part_number=part_number,
                revision_number=revision_number
            )
            unit_ids.append(unit_result.id)
            serial_numbers.append(serial_number)
        
        # Users can delete units
        result = client.units.delete(serial_numbers=serial_numbers)
        assert_delete_units_success(result)
        
        # All units should be deleted
        deleted_ids = result.ids
        for unit_id in unit_ids:
            assert unit_id in deleted_ids
        
        assert len(deleted_ids) == len(unit_ids)

    def test_delete_preserves_other_units(self, client: TofuPilot, auth_type: str, timestamp: str):
        """Test that deleting units doesn't affect other units."""
        if auth_type == "station":
            # Stations have limited access to delete units
            fake_serial_number = "FAKE-UNIT-007"
            with assert_station_access_limited("delete unit while preserving others"):
                client.units.delete(serial_numbers=[fake_serial_number])
            return
            
        # Create test data: part, revision, and multiple units
        part_number = f"DELETE-PRESERVE-PART-{timestamp}"
        revision_number = f"REV-{timestamp}"
        
        # Create part first
        client.parts.create(
            number=part_number,
            name=f"Test Part for Delete Preserve {timestamp}"
        )
        
        # Create revision for the part
        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )
        
        # Create units - one to delete, one to preserve
        serial_to_delete = f"UNIT-DELETE-{timestamp}"
        serial_to_preserve = f"UNIT-PRESERVE-{timestamp}"
        
        unit_to_delete = client.units.create(
            serial_number=serial_to_delete,
            part_number=part_number,
            revision_number=revision_number
        )
        
        unit_to_preserve = client.units.create(
            serial_number=serial_to_preserve,
            part_number=part_number,
            revision_number=revision_number
        )
        
        # Users can delete units
        result = client.units.delete(serial_numbers=[serial_to_delete])
        deleted_ids = result.ids
        
        # Only the targeted unit should be deleted
        assert unit_to_delete.id in deleted_ids
        assert unit_to_preserve.id not in deleted_ids
        
        # Verify preserved unit still exists
        units_list = client.units.list(serial_numbers=[serial_to_preserve])
        assert len(units_list.data) == 1
        assert units_list.data[0].id == unit_to_preserve.id