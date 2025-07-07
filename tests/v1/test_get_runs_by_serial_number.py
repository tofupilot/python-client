"""
Test get_runs_by_serial_number functionality against local TofuPilot server running on localhost:3000.

This test is designed to run against a local development instance of TofuPilot.
It requires:
1. TofuPilot server running on http://localhost:3000
2. Valid API key set in TOFUPILOT_API_KEY environment variable
3. Network connectivity to localhost
4. Existing runs and units in the database for comprehensive testing
"""

import pytest
from typing import List, Dict, Any

from tofupilot.client import TofuPilotClient
from .utils import client, assert_get_runs_by_serial_number_success


class TestGetRunsBySerialNumber:
    """Test suite for the get_runs_by_serial_number endpoint."""

    def test_valid_serial_number(self, client: TofuPilotClient):
        """Test getting runs for a valid serial number."""
        # Use a known serial number that exists in the database
        test_serial_number = "MULTIDIM_001"
        
        result = client.get_runs_by_serial_number(test_serial_number)
        assert_get_runs_by_serial_number_success(result)
        
        # Verify response structure
        assert isinstance(result, dict)
        assert "runs" in result
        assert isinstance(result["runs"], list)
        
        # If there are runs, verify they have the expected structure
        for run in result["runs"]:
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
        
        result = client.get_runs_by_serial_number(nonexistent_serial)
        assert_get_runs_by_serial_number_success(result)
        
        # Should return empty runs but still be successful
        assert isinstance(result["runs"], list)
        assert len(result["runs"]) == 0

    def test_empty_serial_number(self, client: TofuPilotClient):
        """Test behavior with empty serial number."""
        result = client.get_runs_by_serial_number("")
        
        # This might succeed with empty results or fail depending on API validation
        # Check if it's a success or error response
        if result.get("success") is True:
            assert_get_runs_by_serial_number_success(result)
            assert isinstance(result["runs"], list)
        else:
            # If it fails, it should be a proper error response
            assert result.get("success") is False
            assert "error" in result

    def test_special_characters_in_serial_number(self, client: TofuPilotClient):
        """Test serial number with special characters."""
        special_serial = "SN-TEST-ÄÖÜ@#$%"
        
        result = client.get_runs_by_serial_number(special_serial)
        assert_get_runs_by_serial_number_success(result)
        
        # Should handle special characters gracefully
        assert isinstance(result["runs"], list)

    def test_very_long_serial_number(self, client: TofuPilotClient):
        """Test with a very long serial number."""
        long_serial = "SN-" + "A" * 1000  # Very long serial number
        
        result = client.get_runs_by_serial_number(long_serial)
        
        # Should either succeed with empty results or fail gracefully
        if result.get("success") is True:
            assert_get_runs_by_serial_number_success(result)
            assert isinstance(result["runs"], list)
        else:
            assert result.get("success") is False
            assert "error" in result

    def test_response_structure(self, client: TofuPilotClient):
        """Test that response has expected structure."""
        test_serial_number = "MULTIDIM_001"
        
        result = client.get_runs_by_serial_number(test_serial_number)
        assert_get_runs_by_serial_number_success(result)
        
        # Check basic response structure
        assert isinstance(result, dict)
        assert "success" in result
        assert "runs" in result
        assert result["success"] is True
        assert isinstance(result["runs"], list)

    def test_run_data_structure(self, client: TofuPilotClient):
        """Test that individual run objects have expected structure when present."""
        test_serial_number = "MULTIDIM_001"
        
        result = client.get_runs_by_serial_number(test_serial_number)
        assert_get_runs_by_serial_number_success(result)
        
        # If there are runs, check their structure
        if result["runs"]:
            run = result["runs"][0]  # Check first run
            
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
        result1 = client.get_runs_by_serial_number(test_serial_number)
        result2 = client.get_runs_by_serial_number(test_serial_number)
        
        assert_get_runs_by_serial_number_success(result1)
        assert_get_runs_by_serial_number_success(result2)
        
        # Results should be consistent
        assert len(result1["runs"]) == len(result2["runs"])

    @pytest.mark.parametrize("serial_format", [
        "SN-001",
        "UNIT_001",
        "123456789",
        "SN-2024-TEST-001",
        "sn-lowercase-test"
    ])
    def test_various_serial_number_formats(self, client: TofuPilotClient, serial_format: str):
        """Test various serial number formats."""
        result = client.get_runs_by_serial_number(serial_format)
        assert_get_runs_by_serial_number_success(result)
        
        # Should handle all formats gracefully
        assert isinstance(result["runs"], list)