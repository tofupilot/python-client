"""Test part listing, search, pagination, and sorting."""

import uuid

from tofupilot.v2 import TofuPilot
from ..utils import assert_create_part_success, assert_get_parts_success


class TestListParts:
    """Test part listing functionality."""

    def test_list_all_parts(self, client: TofuPilot, auth_type: str) -> None:
        """Test basic listing of parts."""
        result = client.parts.list(limit=5)
        assert_get_parts_success(result)
        assert len(result.data) <= 5
        assert hasattr(result.meta, "has_more")
        assert hasattr(result.meta, "next_cursor")

    def test_list_with_search_query(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test filtering parts by search query."""
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"SEARCH-PART-{unique_id}-{timestamp}"
        name = f"SearchTest Part {unique_id}"
        create_result = client.parts.create(number=part_number, name=name)
        assert_create_part_success(create_result)

        result = client.parts.list(search_query=part_number)
        assert_get_parts_success(result)

        found_ids = [p.id for p in result.data]
        assert create_result.id in found_ids

    def test_list_pagination(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test cursor-based pagination."""
        for i in range(3):
            unique_id = str(uuid.uuid4())[:8]
            client.parts.create(number=f"PAGE-PART-{i}-{unique_id}-{timestamp}")

        page1 = client.parts.list(limit=1)
        assert len(page1.data) == 1
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None

        page2 = client.parts.list(limit=1, cursor=page1.meta.next_cursor)
        assert len(page2.data) == 1
        assert page2.data[0].id != page1.data[0].id

    def test_list_sort_order(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test that sort_by and sort_order change result ordering."""
        for i in range(2):
            unique_id = str(uuid.uuid4())[:8]
            client.parts.create(number=f"SORT-PART-{i}-{unique_id}-{timestamp}")

        asc_result = client.parts.list(sort_by="created_at", sort_order="asc", limit=2)
        desc_result = client.parts.list(sort_by="created_at", sort_order="desc", limit=2)
        assert_get_parts_success(asc_result)
        assert_get_parts_success(desc_result)

        if len(asc_result.data) >= 2 and len(desc_result.data) >= 2:
            assert asc_result.data[0].id != desc_result.data[0].id
