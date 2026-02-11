"""Test procedure listing, search, pagination, and date filtering."""

import uuid
from datetime import datetime, timedelta, timezone

from tofupilot.v2 import TofuPilot
from ..utils import assert_create_procedure_success, assert_get_procedures_success


class TestListProcedures:
    """Test procedure listing functionality."""

    def test_list_all_procedures(self, client: TofuPilot, auth_type: str) -> None:
        """Test basic listing of procedures."""
        result = client.procedures.list(limit=5)
        assert_get_procedures_success(result)
        assert len(result.data) <= 5

    def test_list_with_search_query(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test filtering procedures by search query."""
        if auth_type == "station":
            # Stations can list but can't create — just verify list works
            result = client.procedures.list(search_query="test", limit=5)
            assert_get_procedures_success(result)
            return

        # Create a procedure with a unique name
        unique_id = str(uuid.uuid4())[:8]
        name = f"SearchTest-{unique_id}-{timestamp}"
        create_result = client.procedures.create(name=name)
        assert_create_procedure_success(create_result)

        # Search by name
        result = client.procedures.list(search_query=name)
        assert_get_procedures_success(result)

        found_ids = [p.id for p in result.data]
        assert create_result.id in found_ids

    def test_list_pagination(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test cursor-based pagination."""
        if auth_type == "station":
            # Stations can list — just verify pagination works
            page1 = client.procedures.list(limit=1)
            assert len(page1.data) <= 1
            return

        # Create 3 procedures to ensure enough data
        for i in range(3):
            unique_id = str(uuid.uuid4())[:8]
            client.procedures.create(name=f"PageTest-{i}-{unique_id}-{timestamp}")

        # First page
        page1 = client.procedures.list(limit=1)
        assert len(page1.data) == 1
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None

        # Second page
        page2 = client.procedures.list(limit=1, cursor=page1.meta.next_cursor)
        assert len(page2.data) == 1
        assert page2.data[0].id != page1.data[0].id

    def test_list_with_date_range_filter(self, client: TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test filtering procedures by created_after / created_before."""
        if auth_type == "station":
            # Stations can list — just verify date filter is accepted
            result = client.procedures.list(
                created_after=datetime.now(timezone.utc) - timedelta(days=1),
                limit=5,
            )
            assert_get_procedures_success(result)
            return

        now = datetime.now(timezone.utc)

        # Create a procedure
        unique_id = str(uuid.uuid4())[:8]
        name = f"DateTest-{unique_id}-{timestamp}"
        create_result = client.procedures.create(name=name)
        assert_create_procedure_success(create_result)

        # Filter with a window that includes now
        result = client.procedures.list(
            search_query=name,
            created_after=now - timedelta(minutes=5),
            created_before=now + timedelta(minutes=5),
        )
        assert_get_procedures_success(result)

        found_ids = [p.id for p in result.data]
        assert create_result.id in found_ids
