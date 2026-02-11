"""Test updating units."""

import uuid

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND, ErrorCONFLICT
from ..utils import assert_update_unit_success, assert_get_unit_success
from ...utils import (
    assert_station_access_forbidden,
    assert_create_run_success,
    get_random_test_dates,
)


class TestUpdateUnit:
    """Test updating units."""

    def test_update_serial_number(self, client: TofuPilot, auth_type: str, create_test_unit, timestamp) -> None:
        """Test updating a unit's serial number."""
        if auth_type == "station":
            with assert_station_access_forbidden("update unit serial"):
                client.units.update(serial_number="any", new_serial_number="any")
            return

        unit_id, serial, _ = create_test_unit("UPD-SN")
        new_serial = f"UPD-SN-NEW-{timestamp}"

        result = client.units.update(
            serial_number=serial,
            new_serial_number=new_serial,
        )
        assert_update_unit_success(result)
        assert result.id == unit_id

        # Verify new serial via get
        unit = client.units.get(serial_number=new_serial)
        assert_get_unit_success(unit)
        assert unit.id == unit_id
        assert unit.serial_number == new_serial

    def test_update_part_revision(self, client: TofuPilot, auth_type: str, create_test_unit, timestamp) -> None:
        """Test moving a unit to a different part/revision."""
        if auth_type == "station":
            with assert_station_access_forbidden("update unit part"):
                client.units.update(serial_number="any", part_number="any", revision_number="any")
            return

        unit_id, serial, _ = create_test_unit("UPD-REV")

        # Create new part and revision
        new_part = f"UPD-REV-NEW-PART-{timestamp}"
        new_rev = f"UPD-REV-NEW-REV-{timestamp}"
        client.parts.create(number=new_part, name=f"New Part {timestamp}")
        client.parts.revisions.create(part_number=new_part, number=new_rev)

        result = client.units.update(
            serial_number=serial,
            part_number=new_part,
            revision_number=new_rev,
        )
        assert_update_unit_success(result)

        unit = client.units.get(serial_number=serial)
        assert unit.part.number == new_part
        assert unit.part.revision.number == new_rev

    def test_update_batch_assignment(self, client: TofuPilot, auth_type: str, create_test_unit, timestamp, procedure_id: str) -> None:
        """Test assigning a batch to a unit via update."""
        if auth_type == "station":
            with assert_station_access_forbidden("update unit batch"):
                client.units.update(serial_number="any", batch_number="any")
            return

        unit_id, serial, _ = create_test_unit("UPD-BATCH")
        batch_number = f"BATCH-{timestamp}"

        # Create the batch by making a run with it (batches are auto-created by runs)
        started_at, ended_at = get_random_test_dates()
        client.runs.create(
            serial_number=f"BATCH-INIT-{timestamp}",
            procedure_id=procedure_id,
            part_number=f"UPD-BATCH-INIT-PART-{timestamp}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
            batch_number=batch_number,
        )

        result = client.units.update(
            serial_number=serial,
            batch_number=batch_number,
        )
        assert_update_unit_success(result)

        unit = client.units.get(serial_number=serial)
        assert unit.batch is not None
        assert unit.batch.number == batch_number

    def test_update_nonexistent_unit(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating a unit that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("update nonexistent unit"):
                client.units.update(serial_number="nonexistent", new_serial_number="anything")
            return

        fake_serial = f"NONEXISTENT-{uuid.uuid4().hex[:8]}"

        with pytest.raises(ErrorNOTFOUND):
            client.units.update(
                serial_number=fake_serial,
                new_serial_number="anything",
            )

    def test_update_duplicate_serial(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test updating to a serial number that already exists."""
        if auth_type == "station":
            with assert_station_access_forbidden("update duplicate serial"):
                client.units.update(serial_number="any", new_serial_number="any")
            return

        _, serial_a, _ = create_test_unit("UPD-DUP-A")
        _, serial_b, _ = create_test_unit("UPD-DUP-B")

        with pytest.raises(ErrorCONFLICT):
            client.units.update(
                serial_number=serial_a,
                new_serial_number=serial_b,
            )
