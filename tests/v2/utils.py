"""
Shared test utilities for TofuPilot Python client tests.
"""

import pytest
import os
from unittest.mock import patch

import tofupilot

from trycast import checkcast

from tofupilot.v2.types import (
    GetRunsResponse,
    CreateRunResponse,
    DeleteRunResponse,
    GetUnitsResponse
)



@pytest.fixture(scope="class")
def client(api_key, tofupilot_server_url):
    """Create a client configured for testing."""
    
    # Suppress banner for cleaner test output
    with patch("tofupilot.v2.client._print_version_banner"), \
         patch("tofupilot.v2.client.check_latest_version"):
        
        # Create client pointing to localhost
        client = tofupilot.v2.Client(
            api_key=api_key,
            url=tofupilot_server_url,
        )
        
        # Verify we're pointing to the right URL
        assert client._url == f"{tofupilot_server_url}/api/v2"
        
        return client

# Assertion helper methods
def assert_get_runs_success(result):
    """Helper method to assert successful get_runs response."""
    checkcast(GetRunsResponse, result)

def assert_create_run_success(result):
    """Helper method to assert successful run creation response."""
    checkcast(CreateRunResponse, result)

def assert_delete_runs_success(result):
    """Helper method to assert successful delete_runs response."""
    checkcast(DeleteRunResponse, result)

def assert_get_units_success(result):
    """Helper method to assert successful get_units response."""
    checkcast(GetUnitsResponse, result)