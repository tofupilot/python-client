"""Utility functions for station tests."""

from typing import Any

from trycast import checkcast

from tofupilot.v2.models import (
    StationCreateResponse,
    StationGetResponse,
    StationListResponse,
    StationRemoveResponse,
    StationUpdateResponse,
)


def assert_create_station_success(result: StationCreateResponse) -> None:
    """Assert that a create station response is successful."""
    assert checkcast(StationCreateResponse, result)
    assert len(result.id) > 0


def assert_get_stations_success(result: StationListResponse) -> None:
    """Assert that a list stations response is successful."""
    assert checkcast(StationListResponse, result)


def assert_get_station_success(result: StationGetResponse) -> None:
    """Assert that a get station response is successful."""
    assert checkcast(StationGetResponse, result)


def assert_update_station_success(result: StationUpdateResponse) -> None:
    """Assert that an update station response is successful."""
    assert checkcast(StationUpdateResponse, result)


def assert_remove_station_success(result: StationRemoveResponse) -> None:
    """Assert that a remove station response is successful."""
    assert checkcast(StationRemoveResponse, result)


def assert_link_procedure_success(result: Any) -> None:
    """Assert that a link procedure response is successful."""
    assert hasattr(result, 'station_id')
    assert hasattr(result, 'procedure_id')
    assert result.station_id is not None
    assert result.procedure_id is not None
    assert isinstance(result.station_id, str)
    assert isinstance(result.procedure_id, str)
    assert len(result.station_id) > 0
    assert len(result.procedure_id) > 0


def assert_unlink_procedure_success(result: Any) -> None:
    """Assert that an unlink procedure response is successful."""
    assert hasattr(result, 'station_id')
    assert hasattr(result, 'procedure_id')
    assert result.station_id is not None
    assert result.procedure_id is not None
    assert isinstance(result.station_id, str)
    assert isinstance(result.procedure_id, str)
    assert len(result.station_id) > 0
    assert len(result.procedure_id) > 0
