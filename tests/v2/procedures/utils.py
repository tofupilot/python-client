"""Utility functions for procedure tests."""

from trycast import checkcast

from typing import Optional
from tofupilot.v2 import TofuPilot
from tofupilot.v2.models.procedure_createop import ProcedureCreateResponse
from tofupilot.v2.models.procedure_listop import ProcedureListResponse, ProcedureListData
from tofupilot.v2.models.procedure_updateop import ProcedureUpdateResponse
from tofupilot.v2.models.procedure_deleteop import ProcedureDeleteResponse


def assert_create_procedure_success(result: ProcedureCreateResponse) -> None:
    """Assert that procedure create response is valid."""
    assert checkcast(ProcedureCreateResponse, result)
    assert len(result.id) > 0


def assert_get_procedures_success(result: ProcedureListResponse) -> None:
    """Assert that procedure list response is valid."""
    assert checkcast(ProcedureListResponse, result)
    for procedure in result.data:
        assert len(procedure.id) > 0


def assert_update_procedure_success(result: ProcedureUpdateResponse) -> None:
    """Assert that procedure update response is valid."""
    assert checkcast(ProcedureUpdateResponse, result)
    assert len(result.id) > 0


def assert_delete_procedure_success(result: ProcedureDeleteResponse) -> None:
    """Assert that procedure delete response is valid."""
    assert checkcast(ProcedureDeleteResponse, result)
    assert len(result.id) > 0


def get_procedure_by_id(client: TofuPilot, procedure_id: str) -> Optional[ProcedureListData]:
    """Fetch a procedure by ID from the list endpoint."""
    # Try with a reasonable limit first
    procedures = client.procedures.list(limit=100)
    proc = next((p for p in procedures.data if p.id == procedure_id), None)
    
    if proc is None and procedures.meta.has_more:
        # If not found and there are more, try with a larger limit
        procedures = client.procedures.list(limit=500)
        proc = next((p for p in procedures.data if p.id == procedure_id), None)
    
    return proc