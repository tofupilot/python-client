"""Test batch list filtering and pagination."""

import uuid
from datetime import datetime, timedelta, timezone

from tofupilot.v2 import TofuPilot
from ..utils import assert_get_batches_success
from ...utils import get_random_test_dates


class TestListBatches:
    """Test batch list filtering and pagination."""

    def test_list_all_batches(self, client: TofuPilot, timestamp) -> None:
        """Test listing batches returns paginated results."""
        batch_number = f"LIST-ALL-{timestamp}-{uuid.uuid4().hex[:8]}"
        client.batches.create(number=batch_number)

        result = client.batches.list(limit=10)
        assert_get_batches_success(result)
        assert len(result.data) > 0
        assert hasattr(result.meta, "has_more")
        assert hasattr(result.meta, "next_cursor")

    def test_list_with_number_filter(self, client: TofuPilot, timestamp) -> None:
        """Test filtering batches by number."""
        batch_number = f"LIST-NUM-{timestamp}-{uuid.uuid4().hex[:8]}"
        create_result = client.batches.create(number=batch_number)

        result = client.batches.list(numbers=[batch_number])
        assert_get_batches_success(result)

        result_ids = [b.id for b in result.data]
        assert create_result.id in result_ids

    def test_list_with_part_number_filter(self, client: TofuPilot, procedure_id: str, timestamp) -> None:
        """Test filtering batches by part number of associated units."""
        batch_number = f"LIST-PN-{timestamp}-{uuid.uuid4().hex[:8]}"
        part_number = f"LIST-PN-PART-{timestamp}-{uuid.uuid4().hex[:8]}"

        # Associate batch with part via a run (runs auto-create batch/unit linkage)
        started_at, ended_at = get_random_test_dates()
        client.runs.create(
            serial_number=f"LIST-PN-UNIT-{timestamp}-{uuid.uuid4().hex[:8]}",
            procedure_id=procedure_id,
            part_number=part_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
            batch_number=batch_number,
        )

        result = client.batches.list(part_numbers=[part_number])
        assert_get_batches_success(result)

        result_numbers = [b.number for b in result.data]
        assert batch_number in result_numbers

    def test_list_with_search_query(self, client: TofuPilot, timestamp) -> None:
        """Test filtering batches by search query."""
        unique = uuid.uuid4().hex[:8]
        batch_number = f"LIST-SEARCH-{timestamp}-{unique}"
        client.batches.create(number=batch_number)

        result = client.batches.list(search_query=batch_number)
        assert_get_batches_success(result)

        result_numbers = [b.number for b in result.data]
        assert batch_number in result_numbers

    def test_list_pagination(self, client: TofuPilot, timestamp) -> None:
        """Test cursor-based pagination."""
        numbers = []
        for i in range(3):
            num = f"LIST-PG-{i}-{timestamp}-{uuid.uuid4().hex[:8]}"
            client.batches.create(number=num)
            numbers.append(num)

        # First page
        page1 = client.batches.list(numbers=numbers, limit=1)
        assert len(page1.data) == 1
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None

        # Second page
        page2 = client.batches.list(
            numbers=numbers,
            limit=1,
            cursor=page1.meta.next_cursor,
        )
        assert len(page2.data) == 1
        assert page2.data[0].id != page1.data[0].id

    def test_list_with_ids_filter(self, client: TofuPilot, timestamp) -> None:
        """Test filtering batches by specific IDs."""
        batch_number = f"LIST-IDS-{timestamp}-{uuid.uuid4().hex[:8]}"
        create_result = client.batches.create(number=batch_number)

        result = client.batches.list(ids=[create_result.id])
        assert_get_batches_success(result)
        assert len(result.data) == 1
        assert result.data[0].id == create_result.id

    def test_list_with_created_at_date_range(self, client: TofuPilot, timestamp) -> None:
        """Test filtering batches by created_after and created_before."""
        now = datetime.now(timezone.utc)
        batch_number = f"LIST-CDATE-{timestamp}-{uuid.uuid4().hex[:8]}"
        create_result = client.batches.create(number=batch_number)

        result = client.batches.list(
            ids=[create_result.id],
            created_after=now - timedelta(minutes=5),
            created_before=now + timedelta(minutes=5),
        )
        assert_get_batches_success(result)
        assert len(result.data) == 1
        assert result.data[0].id == create_result.id

    def test_list_with_revision_numbers_filter(self, client: TofuPilot, procedure_id: str, timestamp) -> None:
        """Test filtering batches by revision number of associated units."""
        unique = uuid.uuid4().hex[:8]
        batch_number = f"LIST-REV-{timestamp}-{unique}"
        part_number = f"LIST-REV-PART-{timestamp}-{unique}"
        revision_number = f"LIST-REV-REV-{timestamp}-{unique}"

        # Create part and revision explicitly
        client.parts.create(number=part_number, name=f"Part RevBatch {unique}")
        client.parts.revisions.create(part_number=part_number, number=revision_number)

        # Associate batch with unit via a run
        started_at, ended_at = get_random_test_dates()
        client.runs.create(
            serial_number=f"LIST-REV-UNIT-{timestamp}-{unique}",
            procedure_id=procedure_id,
            part_number=part_number,
            revision_number=revision_number,
            batch_number=batch_number,
            started_at=started_at,
            outcome="PASS",
            ended_at=ended_at,
        )

        result = client.batches.list(revision_numbers=[revision_number])
        assert_get_batches_success(result)

        result_numbers = [b.number for b in result.data]
        assert batch_number in result_numbers

    def test_list_sort_order(self, client: TofuPilot, timestamp) -> None:
        """Test that sort_by and sort_order change result ordering."""
        numbers = []
        for i in range(2):
            num = f"LIST-SORT-{i}-{timestamp}-{uuid.uuid4().hex[:8]}"
            client.batches.create(number=num)
            numbers.append(num)

        asc = client.batches.list(
            numbers=numbers,
            sort_by="created_at",
            sort_order="asc",
        )
        assert len(asc.data) >= 2

        desc = client.batches.list(
            numbers=numbers,
            sort_by="created_at",
            sort_order="desc",
        )
        assert len(desc.data) >= 2

        assert asc.data[0].id != desc.data[0].id
