"""Test batch listing with units information."""

import pytest
from typing import List, Tuple, Dict
from datetime import datetime, timezone, timedelta
from tofupilot.v2 import TofuPilot, models
from ..utils import assert_create_batch_success, assert_get_batches_success
from ...utils import assert_create_run_success


class TestBatchesWithUnits:
    """Test batch listing including associated units."""
    
    @pytest.fixture
    def test_batches_with_units_data(self, client: TofuPilot, procedure_id: str, timestamp) -> Tuple[List[models.BatchCreateResponse], Dict[str, List[str]]]:
        """Create test batches with and without units."""
        
        batches: List[models.BatchCreateResponse] = []
        units_map: Dict[str, List[str]] = {}  # Maps batch_id to list of serial numbers
        
        # Create batch with multiple units
        batch1_number = f"BATCH-WITH-UNITS-{timestamp}"
        batch1 = client.batches.create(number=batch1_number)
        assert_create_batch_success(batch1)
        batches.append(batch1)
        
        # Create units for batch1
        batch1_serials = [f"UNIT-{i}-B1-{timestamp}" for i in range(3)]
        units_map[batch1.id] = batch1_serials
        
        for serial in batch1_serials:
            run = client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number=serial,
                part_number="TEST-PCB-001",
                revision_number="REV-A",
                started_at=datetime.now(timezone.utc) - timedelta(minutes=10),
                ended_at=datetime.now(timezone.utc) - timedelta(minutes=5),
                batch_number=batch1_number
            )
            assert_create_run_success(run)
        
        # Create batch without units
        batch2_number = f"BATCH-EMPTY-{timestamp}"
        batch2 = client.batches.create(number=batch2_number)
        assert_create_batch_success(batch2)
        batches.append(batch2)
        units_map[batch2.id] = []
        
        # Create batch with single unit
        batch3_number = f"BATCH-SINGLE-UNIT-{timestamp}"
        batch3 = client.batches.create(number=batch3_number)
        assert_create_batch_success(batch3)
        batches.append(batch3)
        
        batch3_serial = f"UNIT-SINGLE-B3-{timestamp}"
        units_map[batch3.id] = [batch3_serial]
        
        run = client.runs.create(
            outcome="FAIL",
            procedure_id=procedure_id,
            serial_number=batch3_serial,
            part_number="TEST-PCB-002",
            revision_number="REV-B",
            started_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            ended_at=datetime.now(timezone.utc),
            batch_number=batch3_number
        )
        assert_create_run_success(run)
        
        return batches, units_map

    def test_batch_with_multiple_units(self, client: TofuPilot, test_batches_with_units_data: Tuple[List[models.BatchCreateResponse], Dict[str, List[str]]]):
        """Test listing batch that has multiple units."""
        batches, units_map = test_batches_with_units_data
        batch_with_units = batches[0]
        
        result = client.batches.list(ids=[batch_with_units.id])
        assert_get_batches_success(result)
        assert len(result.data) == 1
        
        batch = result.data[0]
        assert batch.id == batch_with_units.id
        assert hasattr(batch, 'units')
        assert len(batch.units) == 3
        
        # Verify unit details
        expected_serials = set(units_map[batch_with_units.id])
        actual_serials = {unit.serial_number for unit in batch.units}
        assert actual_serials == expected_serials
        
        # Check unit properties
        for unit in batch.units:
            assert unit.serial_number in expected_serials
            assert unit.part is not None
            assert unit.part.number == "TEST-PCB-001"
            assert unit.part.revision.number == "REV-A"

    def test_batch_without_units(self, client: TofuPilot, test_batches_with_units_data: Tuple[List[models.BatchCreateResponse], Dict[str, List[str]]]):
        """Test listing batch that has no units."""
        batches, _ = test_batches_with_units_data
        empty_batch = batches[1]
        
        result = client.batches.list(ids=[empty_batch.id])
        assert_get_batches_success(result)
        assert len(result.data) == 1
        
        batch = result.data[0]
        assert batch.id == empty_batch.id
        assert hasattr(batch, 'units')
        assert len(batch.units) == 0

    def test_batch_with_single_unit(self, client: TofuPilot, test_batches_with_units_data: Tuple[List[models.BatchCreateResponse], Dict[str, List[str]]]):
        """Test listing batch that has a single unit."""
        batches, units_map = test_batches_with_units_data
        single_unit_batch = batches[2]
        
        result = client.batches.list(ids=[single_unit_batch.id])
        assert_get_batches_success(result)
        assert len(result.data) == 1
        
        batch = result.data[0]
        assert batch.id == single_unit_batch.id
        assert hasattr(batch, 'units')
        assert len(batch.units) == 1
        
        unit = batch.units[0]
        assert unit.serial_number == units_map[single_unit_batch.id][0]
        assert unit.part.number == "TEST-PCB-002"
        assert unit.part.revision.number == "REV-B"

    def test_multiple_batches_with_units(self, client: TofuPilot, test_batches_with_units_data: Tuple[List[models.BatchCreateResponse], Dict[str, List[str]]]):
        """Test listing multiple batches with their units."""
        batches, units_map = test_batches_with_units_data
        batch_ids = [b.id for b in batches]
        
        result = client.batches.list(ids=batch_ids)
        assert_get_batches_success(result)
        
        # Verify each batch has correct unit count
        for batch in result.data:
            expected_unit_count = len(units_map.get(batch.id, []))
            assert len(batch.units) == expected_unit_count

    def test_batch_units_ordering(self, client: TofuPilot, test_batches_with_units_data: Tuple[List[models.BatchCreateResponse], Dict[str, List[str]]]):
        """Test that units within a batch maintain consistent ordering."""
        batches, _ = test_batches_with_units_data
        batch_with_units = batches[0]
        
        # Get the batch multiple times
        results: List[models.BatchListData] = []
        for _ in range(3):
            result = client.batches.list(ids=[batch_with_units.id])
            assert_get_batches_success(result)
            results.append(result.data[0])
        
        # Verify units are consistently ordered
        first_unit_serials: List[str] = [u.serial_number for u in results[0].units]
        for result in results[1:]:
            current_serials: List[str] = [u.serial_number for u in result.units]
            assert current_serials == first_unit_serials, "Unit ordering should be consistent"

    def test_search_batches_with_units(self, client: TofuPilot, test_batches_with_units_data: Tuple[List[models.BatchCreateResponse], Dict[str, List[str]]]):
        """Test searching batches returns units information."""
        batches, _ = test_batches_with_units_data
        
        result = client.batches.list(search_query="BATCH-WITH-UNITS")
        assert_get_batches_success(result)
        
        # Find our test batch in results
        test_batch_ids = {b.id for b in batches}
        test_batches = [b for b in result.data if b.id in test_batch_ids]
        
        # Should include units information
        for batch in test_batches:
            if "WITH-UNITS" in batch.number:
                assert len(batch.units) > 0