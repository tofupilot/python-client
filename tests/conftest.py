"""Shared test configuration."""

import pytest
from tofupilot import TofuPilotClient


@pytest.fixture
def client():
    """TofuPilot client instance."""
    return TofuPilotClient(
        api_key="1b25a556-a397-4e54-9a77-de18388197ed",
        base_url="http://localhost:3000"
    )


@pytest.fixture
def procedure_id():
    """Procedure ID for testing."""
    return "FVT-3TV"