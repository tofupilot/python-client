"""Tests for Units API endpoints."""

import pytest


class TestUnitsAPI:
    """Test suite for /v1/units endpoints."""

    def test_delete_unit_method_exists(self, client):
        """Test that delete method exists and is callable."""
        assert hasattr(client.units, 'delete')
        assert callable(client.units.delete)

    def test_update_parent_method_exists(self, client):
        """Test that update_parent method exists and is callable."""
        assert hasattr(client.units, 'update_parent')
        assert callable(client.units.update_parent)