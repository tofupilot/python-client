"""Tests for Uploads API endpoints."""

import pytest


class TestUploadsAPI:
    """Test suite for /v1/uploads endpoints."""

    def test_initialize_upload_method_exists(self, client):
        """Test that initialize method exists and is callable."""
        assert hasattr(client.uploads, 'initialize')
        assert callable(client.uploads.initialize)

    def test_sync_upload_method_exists(self, client):
        """Test that sync method exists and is callable."""
        assert hasattr(client.uploads, 'sync')
        assert callable(client.uploads.sync)