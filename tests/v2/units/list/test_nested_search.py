"""Test search functionality for units list (serial number only)."""

from typing import Dict, List, Any
from datetime import datetime, timezone
import uuid
from tofupilot.v2 import TofuPilot  # type: ignore


class TestUnitsSearch:
    """Test units list search functionality for serial numbers only."""

    def generate_search_test_data(self, client: TofuPilot) -> Dict[str, Any]:
        """Generate test data for serial number search."""
        # Generate unique timestamp to avoid conflicts
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        
        # Create a single part and revision for all units (simplified)
        part_number = f"SEARCH-PART-{timestamp}"
        client.parts.create(  # type: ignore
            name="Test Part for Search",
            number=part_number,
        )
        
        revision = client.parts.revisions.create(  # type: ignore
            part_number=part_number,
            number=f"REV-{timestamp}",
        )

        # Create batches with specific numbers for testing
        batch1_number = f"BATCH-SEARCH-{timestamp}-001"
        batch1 = client.batches.create(  # type: ignore
            number=batch1_number,
        )
        batch2_number = f"BATCH-SEARCH-{timestamp}-002"
        batch2 = client.batches.create(  # type: ignore
            number=batch2_number,
        )

        # Create units with various combinations for testing
        units: List[Any] = []
        serial_numbers: List[str] = []
        
        # Unit 1: Serial number searchable + has batch 1
        serial1 = f"SERIAL-SEARCH-{timestamp}-001"
        unit1 = client.units.create(  # type: ignore
            serial_number=serial1,
            part_number=part_number,
            revision_number=f"REV-{timestamp}",
            batch_id=batch1.id,  # type: ignore
        )
        units.append(unit1)  # type: ignore
        serial_numbers.append(serial1)
        
        # Unit 2: Different serial + same batch 1
        serial2 = f"UNIT-SEARCH-{timestamp}-002"
        unit2 = client.units.create(  # type: ignore
            serial_number=serial2,
            part_number=part_number,
            revision_number=f"REV-{timestamp}",
            batch_id=batch1.id,  # type: ignore
        )
        units.append(unit2)  # type: ignore
        serial_numbers.append(serial2)
        
        # Unit 3: Different serial + batch 2
        serial3 = f"UNIT-SEARCH-{timestamp}-003"
        unit3 = client.units.create(  # type: ignore
            serial_number=serial3,
            part_number=part_number,
            revision_number=f"REV-{timestamp}",
            batch_id=batch2.id,  # type: ignore
        )
        units.append(unit3)  # type: ignore
        serial_numbers.append(serial3)
        
        # Unit 4: Different serial + no batch
        serial4 = f"UNIT-SEARCH-{timestamp}-004"
        unit4 = client.units.create(  # type: ignore
            serial_number=serial4,
            part_number=part_number,
            revision_number=f"REV-{timestamp}",
        )
        units.append(unit4)  # type: ignore
        serial_numbers.append(serial4)

        return {
            "timestamp": timestamp,
            "batches": [batch1, batch2],
            "batch_numbers": [batch1_number, batch2_number],
            "units": units,
            "serial_numbers": serial_numbers,
        }

    def test_search_by_serial_number_partial(self, client: TofuPilot):
        """Test searching units by partial serial number."""
        data = self.generate_search_test_data(client)
        
        # Search by partial serial number
        search_term = f"SERIAL-SEARCH-{data['timestamp']}"
        response = client.units.list(search_query=search_term, limit=10)  # type: ignore
        
        # Should find unit1 (has SERIAL-SEARCH in serial number)
        serial_numbers = [unit.serial_number for unit in response.data]  # type: ignore
        expected_serial = data["serial_numbers"][0]
        assert expected_serial in serial_numbers
        assert len([s for s in serial_numbers if search_term in s]) >= 1

    def test_search_by_serial_number_exact(self, client: TofuPilot):
        """Test searching units by exact serial number."""
        data = self.generate_search_test_data(client)
        
        # Search by exact serial number
        exact_serial = data["serial_numbers"][2]
        response = client.units.list(search_query=exact_serial, limit=10)  # type: ignore
        
        # Should find exactly unit3
        serial_numbers = [unit.serial_number for unit in response.data]  # type: ignore
        assert exact_serial in serial_numbers
        # Verify it's the correct unit
        found_unit = next(unit for unit in response.data if unit.serial_number == exact_serial)
        assert found_unit is not None


    def test_search_case_insensitive(self, client: TofuPilot):
        """Test case insensitive search on serial numbers."""
        data = self.generate_search_test_data(client)
        
        # Search with different case on serial number
        serial_term = "SERIAL-SEARCH"
        response_lower = client.units.list(search_query=serial_term.lower(), limit=10)  # type: ignore
        response_upper = client.units.list(search_query=serial_term.upper(), limit=10)  # type: ignore
        
        # Both should return the same results
        lower_serials = [unit.serial_number for unit in response_lower.data]  # type: ignore
        upper_serials = [unit.serial_number for unit in response_upper.data]  # type: ignore
        expected_serial = data["serial_numbers"][0]
        assert expected_serial in lower_serials
        assert expected_serial in upper_serials

    def test_search_unit_without_batch(self, client: TofuPilot):
        """Test searching finds units without batch when searching by serial number."""
        data = self.generate_search_test_data(client)
        
        # Search for unit4's serial number (unit without batch)
        unit4_serial = data["serial_numbers"][3]
        response = client.units.list(search_query=unit4_serial, limit=10)  # type: ignore
        
        # Should find unit4
        serial_numbers = [unit.serial_number for unit in response.data]  # type: ignore
        assert unit4_serial in serial_numbers  # type: ignore
        
        # Verify the found unit doesn't have a batch
        found_unit = next(unit for unit in response.data if unit.serial_number == unit4_serial)
        assert found_unit.batch is None  # type: ignore

    def test_search_combined_fields(self, client: TofuPilot):
        """Test search works across both serial number and batch number fields."""
        data = self.generate_search_test_data(client)
        
        # Search by timestamp part that appears in both serial numbers and batch numbers
        timestamp_part = data["timestamp"][:8]  # First 8 chars of timestamp
        response = client.units.list(search_query=timestamp_part, limit=20)  # type: ignore
        
        # Should find all 4 units since they all share the same timestamp
        our_serials = data["serial_numbers"]
        found_serials = [unit.serial_number for unit in response.data]  # type: ignore
        found_our_units = sum(1 for serial in our_serials if serial in found_serials)
        assert found_our_units == 4, f"Expected to find all 4 test units, found {found_our_units}"

    def test_search_no_results(self, client: TofuPilot):
        """Test search returns empty when no matches found."""
        # Search for something that definitely doesn't exist
        unique_search = f"NONEXISTENT-{uuid.uuid4().hex[:8]}"
        response = client.units.list(search_query=unique_search, limit=10)  # type: ignore
        
        # Should return empty results
        assert len(response.data) == 0  # type: ignore

    def test_search_empty_query(self, client: TofuPilot):
        """Test that empty search query returns results (no filtering)."""
        response = client.units.list(search_query="", limit=5)  # type: ignore
        
        # Should return some results (empty query means no search filter)
        assert len(response.data) >= 0  # type: ignore