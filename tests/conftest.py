"""Shared test configuration."""

import pytest
from tofupilot import TofuPilotClient


@pytest.fixture
def client():
    """TofuPilot client instance."""
    return TofuPilotClient(
        api_key="76978854-ee7e-45ac-ba51-394103fdcc4a",
        base_url="http://localhost:3000"
    )


@pytest.fixture
def procedure_id():
    """Procedure ID for testing."""
    return "default"