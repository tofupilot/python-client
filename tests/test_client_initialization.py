"""Tests for TofuPilot client initialization and configuration."""

import pytest
from tofupilot import TofuPilotClient


class TestClientInitialization:
    """Test suite for client setup and configuration."""

    def test_client_creation_with_required_params(self):
        """Test client can be created with required parameters."""
        client = TofuPilotClient(api_key="test_key", base_url="http://localhost:3000")
        assert client is not None

    def test_client_has_all_api_endpoints(self, client):
        """Test that client has all expected API endpoint attributes."""
        assert hasattr(client, 'runs')
        assert hasattr(client, 'units')
        assert hasattr(client, 'uploads')
        assert hasattr(client, 'streaming')
        assert hasattr(client, 'imports')

    def test_base_url_auto_append_api_v1(self):
        """Test that /api/v1 is automatically appended to base_url."""
        client = TofuPilotClient(api_key="test_key", base_url="http://localhost:3000")
        assert client._base_url == "http://localhost:3000/api/v1"

    def test_base_url_with_trailing_slash(self):
        """Test base_url handling with trailing slash."""
        client = TofuPilotClient(api_key="test_key", base_url="http://localhost:3000/")
        assert client._base_url == "http://localhost:3000/api/v1"

    def test_base_url_already_has_api_v1(self):
        """Test base_url when it already includes /api/v1."""
        client = TofuPilotClient(api_key="test_key", base_url="http://localhost:3000/api/v1")
        assert client._base_url == "http://localhost:3000/api/v1"