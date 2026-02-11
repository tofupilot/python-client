"""Test runs list filtering, pagination, and sorting."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from tofupilot.v2 import TofuPilot
from ...utils import (
    assert_create_run_success,
    assert_get_runs_success,
    get_random_test_dates,
)


class TestListRuns:
    """Test runs list filtering, pagination, and sorting."""

    def test_list_with_outcome_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by outcome."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-OUTCOME-{unique_id}"

        # Create a PASS run
        started_at, ended_at = get_random_test_dates()
        pass_result = client.runs.create(
            serial_number=f"SN-PASS-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(pass_result)

        # Create a FAIL run
        started_at, ended_at = get_random_test_dates()
        fail_result = client.runs.create(
            serial_number=f"SN-FAIL-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="FAIL",
            ended_at=ended_at,
        )
        assert_create_run_success(fail_result)

        # Filter by PASS only, scoped to our part number
        result = client.runs.list(
            outcomes=["PASS"],
            part_numbers=[part_number],
        )
        assert_get_runs_success(result)

        result_ids = [r.id for r in result.data]
        assert pass_result.id in result_ids
        assert fail_result.id not in result_ids

    def test_list_with_procedure_id_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by procedure ID."""
        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]

        client.runs.create(
            serial_number=f"SN-PROC-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-PROC-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )

        result = client.runs.list(procedure_ids=[procedure_id], limit=10)
        assert_get_runs_success(result)

        for run in result.data:
            assert run.procedure.id == procedure_id

    def test_list_with_serial_number_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by serial number."""
        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]
        serial = f"SN-FILTER-{unique_id}"

        create_result = client.runs.create(
            serial_number=serial,
            procedure_id=procedure_id,
            part_number=f"PART-FILTER-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        result = client.runs.list(serial_numbers=[serial])
        assert_get_runs_success(result)

        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_with_part_number_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by part number."""
        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]
        part = f"PART-LIST-{unique_id}"

        create_result = client.runs.create(
            serial_number=f"SN-PARTFILT-{unique_id}",
            procedure_id=procedure_id,
            part_number=part,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        result = client.runs.list(part_numbers=[part])
        assert_get_runs_success(result)

        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_with_date_range_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by started_after and started_before."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-DATE-{unique_id}"
        now = datetime.now(timezone.utc)

        # Create a run with a known start time
        started_at = now - timedelta(hours=1)
        ended_at = now - timedelta(minutes=55)

        create_result = client.runs.create(
            serial_number=f"SN-DATE-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        # Filter with a window around the run's start time
        result = client.runs.list(
            part_numbers=[part_number],
            started_after=now - timedelta(hours=2),
            started_before=now,
        )
        assert_get_runs_success(result)

        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_with_created_by_user_filter(self, client: TofuPilot, auth_type: str, procedure_id: str) -> None:
        """Test filtering runs by created_by_user_ids."""
        if auth_type == "station":
            return

        started_at, ended_at = get_random_test_dates()
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-CREATED-{unique_id}"

        create_result = client.runs.create(
            serial_number=f"SN-CREATED-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        # Get run to find the creator user ID
        run = client.runs.get(id=create_result.id)
        assert run.created_by_user is not None
        user_id = run.created_by_user.id

        # Scope by part_number to avoid pagination issues
        result = client.runs.list(
            created_by_user_ids=[user_id],
            part_numbers=[part_number],
        )
        assert_get_runs_success(result)

        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_with_duration_range(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by duration_min and duration_max."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-DUR-{unique_id}"

        # Create a run with a 5-minute duration
        now = datetime.now(timezone.utc)
        started_at = now - timedelta(minutes=5)
        ended_at = now

        create_result = client.runs.create(
            serial_number=f"SN-DUR-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        # Filter: 4 min < duration < 6 min
        result = client.runs.list(
            part_numbers=[part_number],
            duration_min="PT4M",
            duration_max="PT6M",
        )
        assert_get_runs_success(result)

        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_pagination(self, client: TofuPilot, procedure_id: str) -> None:
        """Test cursor-based pagination."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-PAGE-{unique_id}"

        # Create 3 runs
        run_ids = []
        for i in range(3):
            started_at, ended_at = get_random_test_dates()
            result = client.runs.create(
                serial_number=f"SN-PAGE-{i}-{unique_id}",
                procedure_id=procedure_id,
                part_number=part_number,
                started_at=started_at,
                outcome="PASS",
                ended_at=ended_at,
            )
            assert_create_run_success(result)
            run_ids.append(result.id)

        # First page: limit=1
        page1 = client.runs.list(part_numbers=[part_number], limit=1)
        assert len(page1.data) == 1
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None

        # Second page
        page2 = client.runs.list(
            part_numbers=[part_number],
            limit=1,
            cursor=page1.meta.next_cursor,
        )
        assert len(page2.data) == 1
        assert page2.data[0].id != page1.data[0].id

    def test_list_sort_order(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that sort_order changes result ordering."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-SORT-{unique_id}"
        now = datetime.now(timezone.utc)

        # Create 2 runs with different start times
        early_result = client.runs.create(
            serial_number=f"SN-SORT-EARLY-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=now - timedelta(hours=2),
            outcome="PASS",
            ended_at=now - timedelta(hours=1, minutes=55),
        )
        assert_create_run_success(early_result)

        late_result = client.runs.create(
            serial_number=f"SN-SORT-LATE-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=now - timedelta(minutes=10),
            outcome="PASS",
            ended_at=now - timedelta(minutes=5),
        )
        assert_create_run_success(late_result)

        # Sort ascending
        asc = client.runs.list(
            part_numbers=[part_number],
            sort_by="started_at",
            sort_order="asc",
        )
        assert len(asc.data) >= 2

        # Sort descending
        desc = client.runs.list(
            part_numbers=[part_number],
            sort_by="started_at",
            sort_order="desc",
        )
        assert len(desc.data) >= 2

        # First result should be different
        assert asc.data[0].id != desc.data[0].id

    def test_list_with_limit(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that limit caps the number of results."""
        result = client.runs.list(
            procedure_ids=[procedure_id],
            limit=2,
        )
        assert len(result.data) <= 2

    def test_list_empty_result(self, client: TofuPilot) -> None:
        """Test that non-matching filters return empty list without error."""
        fake_serial = f"NONEXISTENT-{uuid.uuid4()}"

        result = client.runs.list(serial_numbers=[fake_serial])
        assert isinstance(result.data, list)
        assert len(result.data) == 0

    def test_list_with_ids_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by specific IDs."""
        unique_id = str(uuid.uuid4())[:8]

        started_at, ended_at = get_random_test_dates()
        create_result = client.runs.create(
            serial_number=f"SN-IDS-{unique_id}",
            procedure_id=procedure_id,
            part_number=f"PART-IDS-{unique_id}",
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        result = client.runs.list(ids=[create_result.id])
        assert_get_runs_success(result)
        assert len(result.data) == 1
        assert result.data[0].id == create_result.id

    def test_list_with_procedure_versions_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by procedure version tags."""
        unique_id = str(uuid.uuid4())[:8]
        version_tag = f"v{unique_id}"
        part_number = f"PART-PVER-{unique_id}"

        started_at, ended_at = get_random_test_dates()
        create_result = client.runs.create(
            serial_number=f"SN-PVER-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
            procedure_version=version_tag,
        )
        assert_create_run_success(create_result)

        result = client.runs.list(
            part_numbers=[part_number],
            procedure_versions=[version_tag],
        )
        assert_get_runs_success(result)
        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_with_revision_numbers_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by revision numbers."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-REVF-{unique_id}"
        revision_number = f"REV-{unique_id}"

        # Create part and revision
        client.parts.create(number=part_number, name=f"Part RevFilter {unique_id}")
        client.parts.revisions.create(part_number=part_number, number=revision_number)

        started_at, ended_at = get_random_test_dates()
        create_result = client.runs.create(
            serial_number=f"SN-REVF-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            revision_number=revision_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        result = client.runs.list(
            part_numbers=[part_number],
            revision_numbers=[revision_number],
        )
        assert_get_runs_success(result)
        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_with_ended_at_date_range(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by ended_after and ended_before."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-END-{unique_id}"
        now = datetime.now(timezone.utc)

        started_at = now - timedelta(hours=1)
        ended_at = now - timedelta(minutes=55)

        create_result = client.runs.create(
            serial_number=f"SN-END-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        result = client.runs.list(
            part_numbers=[part_number],
            ended_after=now - timedelta(hours=2),
            ended_before=now,
        )
        assert_get_runs_success(result)
        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_with_created_at_date_range(self, client: TofuPilot, procedure_id: str) -> None:
        """Test filtering runs by created_after and created_before."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-CRE-{unique_id}"
        now = datetime.now(timezone.utc)

        started_at, ended_at = get_random_test_dates()
        create_result = client.runs.create(
            serial_number=f"SN-CRE-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        # The run was just created, so filter around now
        result = client.runs.list(
            part_numbers=[part_number],
            created_after=now - timedelta(minutes=5),
            created_before=now + timedelta(minutes=5),
        )
        assert_get_runs_success(result)
        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_with_created_by_station_filter(self, client: TofuPilot, auth_type: str, procedure_id: str) -> None:
        """Test filtering runs by created_by_station_ids."""
        if auth_type == "user":
            return

        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-STA-{unique_id}"

        started_at, ended_at = get_random_test_dates()
        create_result = client.runs.create(
            serial_number=f"SN-STA-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )
        assert_create_run_success(create_result)

        # Get run to find the station ID
        run = client.runs.get(id=create_result.id)
        assert run.created_by_station is not None
        station_id = run.created_by_station.id

        result = client.runs.list(
            created_by_station_ids=[station_id],
            part_numbers=[part_number],
        )
        assert_get_runs_success(result)
        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids

    def test_list_with_operated_by_filter(self, client: TofuPilot, auth_type: str, procedure_id: str) -> None:
        """Test filtering runs by operated_by_ids."""
        if auth_type == "station":
            return

        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-OPR-{unique_id}"

        # Get current user email to use as operator
        users = client.user.list(current=True)
        assert len(users) > 0
        operator_email = users[0].email

        started_at, ended_at = get_random_test_dates()
        create_result = client.runs.create(
            serial_number=f"SN-OPR-{unique_id}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
            operated_by=operator_email,
        )
        assert_create_run_success(create_result)

        # Get run to find the operator user ID
        run = client.runs.get(id=create_result.id)
        assert run.operated_by is not None
        operator_id = run.operated_by.id

        result = client.runs.list(
            operated_by_ids=[operator_id],
            part_numbers=[part_number],
        )
        assert_get_runs_success(result)
        result_ids = [r.id for r in result.data]
        assert create_result.id in result_ids
