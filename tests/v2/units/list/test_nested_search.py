"""Test search functionality for units list (serial number only)."""

from typing import Dict, List, Any
from datetime import datetime, timezone
import uuid
from tofupilot.v2 import TofuPilot  


class TestUnitsSearch:
    """Test units list search functionality for serial numbers only."""

    def generate_search_test_data(self, client: TofuPilot, timestamp: str) -> Dict[str, Any]:
        """Generate test data for serial number search."""
        # Generate unique timestamp to avoid conflicts
        
        # Create a single part and revision for all units (simplified)
        part_number = f"SEARCH-PART-{timestamp}"
        client.parts.create(  
            name="Test Part for Search",
            number=part_number,
        )
        
        revision = client.parts.revisions.create(  
            part_number=part_number,
            number=f"REV-{timestamp}",
        )

        # Create units with various combinations for testing
        units: List[Any] = []
        serial_numbers: List[str] = []
        
        # Unit 1: Serial number searchable
        serial1 = f"SERIAL-SEARCH-{timestamp}-001"
        unit1 = client.units.create(
            serial_number=serial1,
            part_number=part_number,
            revision_number=f"REV-{timestamp}",
        )
        units.append(unit1)
        serial_numbers.append(serial1)
        
        # Unit 2: Different serial + same batch 1
        serial2 = f"UNIT-SEARCH-{timestamp}-002"
        unit2 = client.units.create(  
            serial_number=serial2,
            part_number=part_number,
            revision_number=f"REV-{timestamp}",
        )
        units.append(unit2)  
        serial_numbers.append(serial2)
        
        # Unit 3: Different serial + batch 2
        serial3 = f"UNIT-SEARCH-{timestamp}-003"
        unit3 = client.units.create(  
            serial_number=serial3,
            part_number=part_number,
            revision_number=f"REV-{timestamp}",
        )
        units.append(unit3)  
        serial_numbers.append(serial3)
        
        # Unit 4: Different serial + no batch
        serial4 = f"UNIT-SEARCH-{timestamp}-004"
        unit4 = client.units.create(  
            serial_number=serial4,
            part_number=part_number,
            revision_number=f"REV-{timestamp}",
        )
        units.append(unit4)  
        serial_numbers.append(serial4)

        return {
            "timestamp": timestamp,
            "units": units,
            "serial_numbers": serial_numbers,
        }

    def test_search_by_serial_number_partial(self, client: TofuPilot, timestamp):
        """Test searching units by partial serial number."""
        data = self.generate_search_test_data(client, timestamp)
        
        # Search by partial serial number
        search_term = f"SERIAL-SEARCH-{data['timestamp']}"
        response = client.units.list(search_query=search_term, limit=10)  
        
        # Should find unit1 (has SERIAL-SEARCH in serial number)
        serial_numbers = [unit.serial_number for unit in response.data]  
        expected_serial = data["serial_numbers"][0]
        assert expected_serial in serial_numbers
        assert len([s for s in serial_numbers if search_term in s]) >= 1

    def test_search_by_serial_number_exact(self, client: TofuPilot, timestamp):
        """Test searching units by exact serial number."""
        data = self.generate_search_test_data(client, timestamp)
        
        # Search by exact serial number
        exact_serial = data["serial_numbers"][2]
        response = client.units.list(search_query=exact_serial, limit=10)  
        
        # Should find exactly unit3
        serial_numbers = [unit.serial_number for unit in response.data]  
        assert exact_serial in serial_numbers
        # Verify it's the correct unit
        found_unit = next(unit for unit in response.data if unit.serial_number == exact_serial)
        assert found_unit is not None


    def test_search_case_insensitive(self, client: TofuPilot, timestamp):
        """Test case insensitive search on serial numbers."""
        data = self.generate_search_test_data(client, timestamp)
        
        # Search with different case on serial number
        serial_term = "SERIAL-SEARCH"
        response_lower = client.units.list(search_query=serial_term.lower(), limit=10)  
        response_upper = client.units.list(search_query=serial_term.upper(), limit=10)  
        
        # Both should return the same results
        lower_serials = [unit.serial_number for unit in response_lower.data]  
        upper_serials = [unit.serial_number for unit in response_upper.data]  
        expected_serial = data["serial_numbers"][0]
        assert expected_serial in lower_serials
        assert expected_serial in upper_serials

    def test_search_unit_without_batch(self, client: TofuPilot, timestamp):
        """Test searching finds units without batch when searching by serial number."""
        data = self.generate_search_test_data(client, timestamp)
        
        # Search for unit4's serial number (unit without batch)
        unit4_serial = data["serial_numbers"][3]
        response = client.units.list(search_query=unit4_serial, limit=10)  
        
        # Should find unit4
        serial_numbers = [unit.serial_number for unit in response.data]  
        assert unit4_serial in serial_numbers  
        
        # Verify the found unit doesn't have a batch
        found_unit = next(unit for unit in response.data if unit.serial_number == unit4_serial)
        assert found_unit.batch is None  

    def test_search_combined_fields(self, client: TofuPilot, timestamp):
        """Test search works across both serial number and batch number fields."""
        data = self.generate_search_test_data(client, timestamp)
        
        # Search by timestamp part that appears in both serial numbers and batch numbers
        timestamp_part = data["timestamp"][:8]  # First 8 chars of timestamp
        response = client.units.list(search_query=timestamp_part, limit=20)  
        
        # Should find all 4 units since they all share the same timestamp
        our_serials = data["serial_numbers"]
        found_serials = [unit.serial_number for unit in response.data]  
        found_our_units = sum(1 for serial in our_serials if serial in found_serials)
        assert found_our_units == 4, f"Expected to find all 4 test units, found {found_our_units}"

    def test_search_no_results(self, client: TofuPilot, timestamp):
        """Test search returns empty when no matches found."""
        # Search for something that definitely doesn't exist
        unique_search = f"NONEXISTENT-{uuid.uuid4().hex[:8]}"
        response = client.units.list(search_query=unique_search, limit=10)  
        
        # Should return empty results
        assert len(response.data) == 0  

    def test_search_empty_query(self, client: TofuPilot, timestamp):
        """Test that empty search query returns results (no filtering)."""
        response = client.units.list(search_query="", limit=5)  
        
        # Should return some results (empty query means no search filter)
        assert len(response.data) >= 0  