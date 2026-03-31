"""Utility functions for procedure version tests."""

from trycast import checkcast

from typing import Optional
from tofupilot.v2 import TofuPilot
from tofupilot.v2.models.procedure_createversionop import ProcedureCreateVersionResponse
# Note: There's no list versions endpoint in the API, versions are accessed individually
from tofupilot.v2.models.procedure_getversionop import ProcedureGetVersionResponse
from tofupilot.v2.models.procedure_deleteversionop import ProcedureDeleteVersionResponse


def assert_create_procedure_version_success(result: ProcedureCreateVersionResponse) -> None:
    """Assert that procedure version create response is valid."""
    assert checkcast(ProcedureCreateVersionResponse, result)
    assert len(result.id) > 0


def assert_get_procedure_version_success(result: ProcedureGetVersionResponse) -> None:
    """Assert that procedure version get response is valid."""
    assert checkcast(ProcedureGetVersionResponse, result)
    assert len(result.id) > 0


# Removed assert_list_procedure_versions_success as there's no list versions endpoint


def assert_delete_procedure_version_success(result: ProcedureDeleteVersionResponse) -> None:
    """Assert that procedure version delete response is valid."""
    assert checkcast(ProcedureDeleteVersionResponse, result)
    assert len(result.id) > 0


def get_procedure_version_by_tag(client: TofuPilot, procedure_id: str, tag: str) -> Optional[ProcedureGetVersionResponse]:
    """Fetch a procedure version by procedure_id and tag."""
    try:
        # Use the get endpoint to fetch a specific version by tag
        version = client.procedures.versions.get(
            procedure_id=procedure_id,
            tag=tag
        )
        return version
    except Exception:
        return None