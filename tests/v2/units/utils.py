"""Utility functions for unit tests."""

from trycast import checkcast

from typing import Optional
from tofupilot.v2.models.unit_deleteop import UnitDeleteResponse
from tofupilot.v2 import TofuPilot
from tofupilot.v2.models.unit_createop import UnitCreateResponse
from tofupilot.v2.models.unit_getop import UnitGetResponse
from tofupilot.v2.models.unit_listop import UnitListResponse, UnitListData
from tofupilot.v2.models.unit_updateop import UnitUpdateResponse


def assert_create_unit_success(result: UnitCreateResponse) -> None:
    """Assert that unit create response is valid."""
    assert checkcast(UnitCreateResponse, result)
    assert len(result.id) > 0


def assert_get_unit_success(result: UnitGetResponse) -> None:
    """Assert that unit get response is valid."""
    assert checkcast(UnitGetResponse, result)
    assert len(result.id) > 0


def assert_get_units_success(result: UnitListResponse) -> None:
    """Assert that unit list response is valid."""
    assert checkcast(UnitListResponse, result)
    for unit in result.data:
        assert len(unit.id) > 0


def assert_update_unit_success(result: UnitUpdateResponse) -> None:
    """Assert that unit update response is valid."""
    assert checkcast(UnitUpdateResponse, result)
    assert len(result.id) > 0


def assert_delete_unit_success(result: UnitDeleteResponse) -> None:
    """Assert that unit delete response is valid."""
    assert checkcast(UnitDeleteResponse, result)
    assert len(result.ids) > 0
    for unit_id in result.ids:
        assert len(unit_id) > 0


def get_unit_by_id(client: TofuPilot, unit_id: str) -> Optional[UnitListData]:
    """Fetch a unit by ID from the list endpoint."""
    # Use the ids parameter to filter directly by ID
    units = client.units.list(ids=[unit_id])
    return units.data[0] if units.data else None