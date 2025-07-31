"""Test get_runs_by_serial_number functionality."""

import pytest

from tofupilot import TofuPilotClient
from ...utils import client, assert_get_runs_success


class TestGetRunsBySerialNumber:
    """Test suite for the get_runs_by_serial_number endpoint."""

    def test_valid_serial_number(self, client: TofuPilotClient):
        """Test getting runs for a valid serial number."""
        # Use a known serial number that exists in the database
        test_serial_number = "MULTIDIM_001"
        
        result = client.get_runs(serial_number=test_serial_number)
        assert_get_runs_success(result)
        
        # If there are runs, verify they have the expected structure
        for run in result["result"]:
            assert isinstance(run, dict)
            assert "id" in run
            assert isinstance(run["id"], str)
            # Each run should be associated with a unit that has the requested serial number
            if "unit" in run and run["unit"]:
                # The unit should have the serial number we requested
                unit = run["unit"]
                if "serialNumber" in unit:
                    assert unit["serialNumber"] == test_serial_number

    def test_nonexistent_serial_number(self, client: TofuPilotClient):
        """Test getting runs for a serial number that doesn't exist."""
        # Use a serial number that should not exist
        nonexistent_serial = "NONEXISTENT-SERIAL-12345"
        
        result = client.get_runs(serial_number=nonexistent_serial)
        assert_get_runs_success(result)
        
        assert len(result["result"]) == 0

    def test_empty_serial_number(self, client: TofuPilotClient):
        """Test behavior with empty serial number."""
        result = client.get_runs(serial_number="")
        
        assert result.get("success") is False

    def test_special_characters_in_serial_number(self, client: TofuPilotClient):
        """Test serial number with special characters."""
        special_serial = "SN-TEST-ÄÖÜ@#$%"
        
        result = client.get_runs(serial_number=special_serial)
        assert_get_runs_success(result)

    def test_very_long_serial_number(self, client: TofuPilotClient):
        """Test with a very long serial number."""
        long_serial = "SN-" + "A" * 1000  # Very long serial number

        just_short_enough_serial = long_serial[:255]
        
        result = client.get_runs(serial_number=just_short_enough_serial)
        assert_get_runs_success(result)

        # TODO: Add failing test with long serial

    def test_response_structure(self, client: TofuPilotClient):
        """Test that response has expected structure."""
        test_serial_number = "MULTIDIM_001"
        
        result = client.get_runs(serial_number=test_serial_number)
        assert_get_runs_success(result)

    def test_run_data_structure(self, client: TofuPilotClient):
        """Test that individual run objects have expected structure when present."""
        test_serial_number = "MULTIDIM_001"
        
        result = client.get_runs(serial_number=test_serial_number)
        assert_get_runs_success(result)
        
        # If there are runs, check their structure
        if result["result"]:
            run = result["result"][0]  # Check first run
            
            # Basic fields that should be present in a run object
            assert "id" in run
            assert isinstance(run["id"], str)
            
            # Optional fields that might be present
            optional_fields = ["outcome", "startedAt", "createdAt", "duration", "procedure", "unit"]
            for field in optional_fields:
                if field in run:
                    assert run[field] is not None or field in ["procedure", "unit"]  # These can be null

    def test_multiple_serial_number_calls(self, client: TofuPilotClient):
        """Test making multiple calls to ensure consistency."""
        test_serial_number = "MULTIDIM_001"
        
        # Make multiple calls
        result1 = client.get_runs(serial_number=test_serial_number)
        result2 = client.get_runs(serial_number=test_serial_number)
        
        assert_get_runs_success(result1)
        assert_get_runs_success(result2)
        
        # Results should be consistent
        assert len(result1["result"]) == len(result2["result"])

    @pytest.mark.parametrize("serial_format", [
        "SN-001",
        "UNIT_001",
        "123456789",
        "SN-2024-TEST-001",
        "sn-lowercase-test"
    ])
    def test_various_serial_number_formats(self, client: TofuPilotClient, serial_format: str):
        """Test various serial number formats."""
        result = client.get_runs(serial_number=serial_format)
        assert_get_runs_success(result)