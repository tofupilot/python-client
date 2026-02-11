"""Test units list filtering, pagination, and sorting."""

import uuid
from datetime import datetime, timedelta, timezone

from tofupilot.v2 import TofuPilot
from ..utils import assert_get_units_success
from ...utils import assert_create_run_success, get_random_test_dates


class TestListUnits:
    """Test units list filtering, pagination, and sorting."""

    def test_list_all_units(self, client: TofuPilot, create_test_unit) -> None:
        """Test listing units returns paginated results."""
        create_test_unit("LIST-ALL")

        result = client.units.list(limit=10)
        assert_get_units_success(result)
        assert len(result.data) > 0
        assert hasattr(result.meta, "has_more")
        assert hasattr(result.meta, "next_cursor")

    def test_list_with_serial_number_filter(self, client: TofuPilot, create_test_unit) -> None:
        """Test filtering units by serial number."""
        unit_id, serial, _ = create_test_unit("LIST-SN")

        result = client.units.list(serial_numbers=[serial])
        assert_get_units_success(result)

        result_ids = [u.id for u in result.data]
        assert unit_id in result_ids

    def test_list_with_part_number_filter(self, client: TofuPilot, create_test_unit, timestamp) -> None:
        """Test filtering units by part number."""
        unit_id, _, _ = create_test_unit("LIST-PN")
        part_number = f"LIST-PN-PART-{timestamp}"

        result = client.units.list(part_numbers=[part_number])
        assert_get_units_success(result)

        result_ids = [u.id for u in result.data]
        assert unit_id in result_ids

    def test_list_with_search_query(self, client: TofuPilot, create_test_unit) -> None:
        """Test filtering units by search query."""
        unit_id, serial, _ = create_test_unit("LIST-SEARCH")

        result = client.units.list(search_query=serial)
        assert_get_units_success(result)

        result_ids = [u.id for u in result.data]
        assert unit_id in result_ids

    def test_list_exclude_units_with_parent(self, client: TofuPilot, create_test_unit) -> None:
        """Test that exclude_units_with_parent filters out child units."""
        parent_id, parent_serial, _ = create_test_unit("LIST-EXCL-P")
        child_id, child_serial, _ = create_test_unit("LIST-EXCL-C")

        client.units.add_child(
            serial_number=parent_serial,
            child_serial_number=child_serial,
        )

        # With exclude filter: child (which has a parent) should not appear
        filtered = client.units.list(
            ids=[parent_id, child_id],
            exclude_units_with_parent=True,
        )
        filtered_ids = [u.id for u in filtered.data]
        assert parent_id in filtered_ids
        assert child_id not in filtered_ids

    def test_list_pagination(self, client: TofuPilot, create_test_unit) -> None:
        """Test cursor-based pagination."""
        serials = []
        for i in range(3):
            _, sn, _ = create_test_unit(f"LIST-PG-{i}")
            serials.append(sn)

        # First page
        page1 = client.units.list(serial_numbers=serials, limit=1)
        assert len(page1.data) == 1
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None

        # Second page
        page2 = client.units.list(
            serial_numbers=serials,
            limit=1,
            cursor=page1.meta.next_cursor,
        )
        assert len(page2.data) == 1
        assert page2.data[0].id != page1.data[0].id

    def test_list_with_ids_filter(self, client: TofuPilot, create_test_unit) -> None:
        """Test filtering units by specific IDs."""
        unit_id, _, _ = create_test_unit("LIST-IDS")

        result = client.units.list(ids=[unit_id])
        assert_get_units_success(result)
        assert len(result.data) == 1
        assert result.data[0].id == unit_id

    def test_list_with_revision_numbers_filter(self, client: TofuPilot, create_test_unit, timestamp) -> None:
        """Test filtering units by revision number."""
        unit_id, _, _ = create_test_unit("LIST-REV")
        revision_number = f"LIST-REV-REV-{timestamp}"

        result = client.units.list(revision_numbers=[revision_number])
        assert_get_units_success(result)

        result_ids = [u.id for u in result.data]
        assert unit_id in result_ids

    def test_list_with_batch_numbers_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering units by batch number."""
        unique_id = str(uuid.uuid4())[:8]
        batch_number = f"BATCH-{unique_id}"

        # Create a unit with a batch via runs.create
        started_at, ended_at = get_random_test_dates()
        run_result = client.runs.create(
            serial_number=f"SN-BATCH-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-BATCH-{unique_id}",
            batch_number=batch_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(run_result)

        result = client.units.list(batch_numbers=[batch_number])
        assert_get_units_success(result)
        assert len(result.data) >= 1

        serials = [u.serial_number for u in result.data]
        assert f"SN-BATCH-{unique_id}" in serials

    def test_list_with_created_at_date_range(self, client: TofuPilot, create_test_unit) -> None:
        """Test filtering units by created_after and created_before."""
        now = datetime.now(timezone.utc)
        unit_id, _, _ = create_test_unit("LIST-CDATE")

        result = client.units.list(
            ids=[unit_id],
            created_after=now - timedelta(minutes=5),
            created_before=now + timedelta(minutes=5),
        )
        assert_get_units_success(result)
        assert len(result.data) == 1
        assert result.data[0].id == unit_id

    def test_list_with_created_by_user_filter(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test filtering units by created_by_user_ids."""
        if auth_type == "station":
            return

        unit_id, serial_number, _ = create_test_unit("LIST-CUSER")

        # Get the unit to find creator user ID
        unit = client.units.get(serial_number=serial_number)
        assert unit.created_by_user is not None
        user_id = unit.created_by_user.id

        result = client.units.list(
            ids=[unit_id],
            created_by_user_ids=[user_id],
        )
        assert_get_units_success(result)
        result_ids = [u.id for u in result.data]
        assert unit_id in result_ids

    def test_list_with_created_by_station_filter(self, client: TofuPilot, auth_type: str, create_test_unit) -> None:
        """Test filtering units by created_by_station_ids."""
        if auth_type == "user":
            return

        unit_id, serial_number, _ = create_test_unit("LIST-CSTA")

        # Get the unit to find creator station ID
        unit = client.units.get(serial_number=serial_number)
        assert unit.created_by_station is not None
        station_id = unit.created_by_station.id

        result = client.units.list(
            ids=[unit_id],
            created_by_station_ids=[station_id],
        )
        assert_get_units_success(result)
        result_ids = [u.id for u in result.data]
        assert unit_id in result_ids

    def test_list_sort_order(self, client: TofuPilot, create_test_unit) -> None:
        """Test that sort_by and sort_order change result ordering."""
        serials = []
        ids = []
        for i in range(2):
            uid, sn, _ = create_test_unit(f"LIST-SORT-{i}")
            ids.append(uid)
            serials.append(sn)

        asc = client.units.list(
            serial_numbers=serials,
            sort_by="created_at",
            sort_order="asc",
        )
        assert len(asc.data) >= 2

        desc = client.units.list(
            serial_numbers=serials,
            sort_by="created_at",
            sort_order="desc",
        )
        assert len(desc.data) >= 2

        assert asc.data[0].id != desc.data[0].id
