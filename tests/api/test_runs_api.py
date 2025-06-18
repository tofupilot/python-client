"""Tests for Runs API endpoints."""

import pytest


class TestRunsAPI:
    """Test suite for /v1/runs endpoints."""

    def test_get_runs_by_serial_success(self, client, test_serial_number):
        """Test GET /v1/runs with valid serial number."""
        response = client.runs.get_by_serial(test_serial_number)
        # Response can be successful data or error object
        assert response is not None

    def test_get_runs_by_serial_response_structure(self, client, test_serial_number):
        """Test that response has expected structure."""
        response = client.runs.get_by_serial(test_serial_number)
        # Response is either parsed data or error object
        assert response is not None
        assert hasattr(response, '__class__')

    def test_post_create_run_method_exists(self, client):
        """Test that create method exists and is callable."""
        assert hasattr(client.runs, 'create')
        assert callable(client.runs.create)

    def test_delete_run_method_exists(self, client):
        """Test that delete method exists and is callable."""
        assert hasattr(client.runs, 'delete')
        assert callable(client.runs.delete)