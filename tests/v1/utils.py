"""
Shared test utilities for TofuPilot Python client tests.
"""

import pytest
import os
from unittest.mock import patch

from tofupilot.client import TofuPilotClient

from trycast import checkcast

from tofupilot.responses.responses import (
    CreateRunResponse,
    GetRunsBySerialNumberResponse,
)



@pytest.fixture(scope="class")
def client(api_key, tofupilot_server_url):
    """Create a client configured for testing."""
    
    # Suppress banner for cleaner test output
    with patch("tofupilot.client.print_version_banner"), \
         patch("tofupilot.client.check_latest_version"):
        
        # Create client pointing to localhost
        client = TofuPilotClient(
            api_key=api_key,
            url=tofupilot_server_url,
        )
        
        # Verify we're pointing to the right URL
        assert client._url == f"{tofupilot_server_url}/api/v1"
        
        return client

# Assertion helper methods

def assert_create_run_success(result):
    """Helper method to assert successful run creation response."""
    assert result["success"], f"Run creation failed: {result}"
    checkcast(CreateRunResponse, result)

def assert_get_runs_by_serial_number_success(result):
    """Helper method to assert successful get_runs_by_serial_number response."""
    assert result["success"], f"Get runs by serial number failed: {result}"
    checkcast(GetRunsBySerialNumberResponse, result)