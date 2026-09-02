"""client_run_ref: a retried upload returns the run already created.

TP-1012: a run upload whose HTTP response never reached the client was
re-POSTed and stored a second, complete run. `client_run_ref` is the
idempotency reference the caller mints BEFORE it sends; a second request with
the same reference and the same payload returns the first run's id instead of
creating another. The server-side behaviour is pinned in detail by
`apps/web/server/trpc/core/runs/create-idempotency.test.ts`; this test pins the
contract as a customer sees it through the SDK.
"""

from tofupilot.v2 import TofuPilot
from ...utils import get_random_test_dates, assert_create_run_success
from ....e2e_tag import uid


def _payload(procedure_id: str, unique: str, ref: str) -> dict:
    started_at, ended_at = get_random_test_dates()
    return {
        "serial_number": f"SN-IDEM-{unique}",
        "procedure_id": procedure_id,
        "part_number": f"PART-IDEM-{unique}",
        "started_at": started_at,
        "ended_at": ended_at,
        "outcome": "PASS",
        "client_run_ref": ref,
    }


def test_same_reference_returns_the_same_run(client: TofuPilot, procedure_id: str):
    """Two creates with one reference and one payload yield one run."""
    unique = uid()
    payload = _payload(procedure_id, unique, f"idem-{unique}")

    first = client.runs.create(**payload)
    assert_create_run_success(first)
    second = client.runs.create(**payload)
    assert_create_run_success(second)

    assert second.id == first.id


def test_omitting_the_reference_creates_a_run_per_request(client: TofuPilot, procedure_id: str):
    """Opting out keeps the historical behaviour: every request is a new run."""
    unique = uid()
    payload = _payload(procedure_id, unique, ref="")
    del payload["client_run_ref"]

    first = client.runs.create(**payload)
    second = client.runs.create(**payload)

    assert second.id != first.id
