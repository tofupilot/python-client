import os
import requests
import pytest
from datetime import datetime, timezone
from typing import Callable, Tuple
from .units.utils import assert_create_unit_success

# Import client fixture from utils to make it available for all tests
from .utils import client, user_client  # pyright: ignore[reportUnusedImport] # noqa: F401

@pytest.fixture
def auth_type(request: pytest.FixtureRequest) -> str:
    """Fixture that provides the auth type (user or station) corresponding to the api_key fixture."""
    if hasattr(request, 'node') and hasattr(request.node, 'callspec'):  # type: ignore[misc]
        return request.node.callspec.params.get('api_key', 'user')  # type: ignore[misc]
    return 'user'

@pytest.fixture
def timestamp():
    return datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')


@pytest.fixture(scope="session", autouse=True)
def ensure_station_linked_to_procedure():
    """Ensure the CI test station is linked to the test procedure before any tests run.

    Uses the internal tRPC endpoint since the V2 API doesn't expose station-procedure linking.
    Idempotent: silently succeeds if already linked.
    """
    url = os.environ.get("TOFUPILOT_URL")
    user_key = os.environ.get("TOFUPILOT_API_KEY_USER")
    procedure_id = os.environ.get("TOFUPILOT_PROCEDURE_ID")
    station_id = os.environ.get("TOFUPILOT_STATION_ID")

    if not all([url, user_key, procedure_id, station_id]):
        return

    headers = {"Authorization": f"Bearer {user_key}", "Content-Type": "application/json"}
    try:
        requests.post(
            f"{url}/api/trpc/station.linkProcedure",
            headers=headers,
            json={"json": {"id": station_id, "procedure_id": procedure_id}},
            timeout=10,
        )
    except Exception:
        pass


@pytest.fixture()
def create_test_unit(client, timestamp) -> Callable[..., Tuple[str, str, str]]:

    def func(prefix: str):
        """Create a test unit and return (unit_id, serial_number, revision_id)."""
        part_number = f"{prefix}-PART-{timestamp}"
        revision_number = f"{prefix}-REV-{timestamp}"
        serial_number = f"{prefix}-{timestamp}"

        # Create part and revision
        client.parts.create(
            number=part_number,
            name=f"Test Part {prefix} {timestamp}"
        )

        revision_result = client.parts.revisions.create(
            part_number=part_number,
            number=revision_number
        )

        # Create unit
        unit_result = client.units.create(
            serial_number=serial_number,
            part_number=part_number,
            revision_number=revision_number,
        )

        assert_create_unit_success(unit_result)
        return unit_result.id, serial_number, revision_result.id

    return func
