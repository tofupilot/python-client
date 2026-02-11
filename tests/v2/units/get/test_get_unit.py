"""Test getting individual unit details."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_get_unit_success
from ...utils import (
    assert_create_run_success,
    get_random_test_dates,
)


class TestGetUnit:
    """Test getting individual unit details."""

    def test_get_unit_by_serial_number(self, client: TofuPilot, create_test_unit, timestamp) -> None:
        """Test getting a unit by serial number and verifying fields."""
        unit_id, serial, _ = create_test_unit("GET-UNIT")

        result = client.units.get(serial_number=serial)
        assert_get_unit_success(result)

        assert result.id == unit_id
        assert result.serial_number == serial
        assert result.created_at is not None
        assert result.part is not None
        assert result.part.number == f"GET-UNIT-PART-{timestamp}"
        assert result.part.revision is not None

    def test_get_nonexistent_unit(self, client: TofuPilot) -> None:
        """Test getting a unit that doesn't exist."""
        fake_serial = f"NONEXISTENT-{uuid.uuid4().hex[:8]}"

        with pytest.raises(ErrorNOTFOUND):
            client.units.get(serial_number=fake_serial)

    def test_get_unit_includes_children(self, client: TofuPilot, create_test_unit) -> None:
        """Test that get unit includes children list."""
        parent_id, parent_serial, _ = create_test_unit("GET-CHILD-P")
        child_id, child_serial, _ = create_test_unit("GET-CHILD-C")

        client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )

        result = client.units.get(serial_number=parent_serial)
        assert_get_unit_success(result)
        assert result.children is not None
        assert len(result.children) >= 1

        child_serials = [c.serial_number for c in result.children]
        assert child_serial in child_serials

    def test_get_unit_includes_parent(self, client: TofuPilot, create_test_unit) -> None:
        """Test that get unit includes parent reference."""
        parent_id, parent_serial, _ = create_test_unit("GET-PAR-P")
        child_id, child_serial, _ = create_test_unit("GET-PAR-C")

        client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )

        result = client.units.get(serial_number=child_serial)
        assert_get_unit_success(result)
        assert result.parent is not None
        assert result.parent.id == parent_id
        assert result.parent.serial_number == parent_serial

    def test_get_unit_includes_runs(self, client: TofuPilot, procedure_id: str, timestamp) -> None:
        """Test that a unit created during a run has created_during populated."""
        serial = f"GET-RUNS-{timestamp}"
        started_at, ended_at = get_random_test_dates()

        run_result = client.runs.create(
            serial_number=serial,
            procedure_id=procedure_id,
            part_number=f"GET-RUNS-PART-{timestamp}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(run_result)

        result = client.units.get(serial_number=serial)
        assert_get_unit_success(result)
        assert result.created_during is not None
        assert result.created_during.id == run_result.id
        assert result.created_during.outcome == "PASS"
