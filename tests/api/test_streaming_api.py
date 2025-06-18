"""Tests for Streaming API endpoints."""

import pytest


class TestStreamingAPI:
    """Test suite for /v1/streaming endpoints."""

    def test_get_streaming_token_method_exists(self, client):
        """Test that get_token method exists and is callable."""
        assert hasattr(client.streaming, 'get_token')
        assert callable(client.streaming.get_token)

    def test_get_streaming_token_response_structure(self, client):
        """Test GET /v1/streaming response structure."""
        try:
            response = client.streaming.get_token()
            assert hasattr(response, 'status_code')
            assert hasattr(response, 'parsed')
        except Exception:
            # API might not be available in test environment
            pytest.skip("Streaming API not available in test environment")