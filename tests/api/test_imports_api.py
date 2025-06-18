"""Tests for Imports API endpoints."""

import pytest


class TestImportsAPI:
    """Test suite for /v1/import endpoints."""

    def test_create_from_file_method_exists(self, client):
        """Test that create_from_file method exists and is callable."""
        assert hasattr(client.imports, 'create_from_file')
        assert callable(client.imports.create_from_file)