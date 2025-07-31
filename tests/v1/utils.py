"""
Shared test utilities for TofuPilot Python client tests.
"""

import pytest
import uuid
from unittest.mock import patch
from typing import Callable, TypedDict, Optional, Literal, List, Dict, Any

import tofupilot
from tofupilot import TofuPilotClient

from trycast import checkcast

# TODO: Use this import once v2 is released
"""
from tofupilot.responses.responses import (
    CreateRunResponse,
    GetRunsResponse,
)
"""

# TEMPORARY
Outcome = Literal["PASS", "FAIL", "ERROR", "TIMEOUT", "ABORTED"]

class _RunUserOptional(TypedDict, total=False):
    image: object
    image_uploaded: object

class _RunUser(_RunUserOptional):
    id: str
    name: Optional[str]

class _RunStationOptional(TypedDict, total=False):
    image: object

class _RunStation(_RunStationOptional, total=False):
    id: str
    name: Optional[str]

class _RunProcedure(TypedDict):
    id: str
    name: str

class _RunUnitBatch(TypedDict):
    id: str
    number: str

class _RunUnitRevisionComponent(TypedDict, total=False):
    id: str
    part_number: str
    name: str

class _RunUnitRevisionOptional(TypedDict, total=False):
    image: Optional[object]

class _RunUnitRevision(_RunUnitRevisionOptional):
    id: str
    identifier: str
    component: Optional[_RunUnitRevisionComponent]

class _RunUnitOptional(TypedDict, total=False):
    batch: Optional[_RunUnitBatch]
    revision: Optional[_RunUnitRevision]

class _RunUnit(_RunUnitOptional):
    id: str
    serial_number: str

class _RunPhaseOptional(TypedDict, total=False):
    outcome: object
    docstring: str
    measurements: List[object]

class _RunPhase(_RunPhaseOptional):
    id: str
    name: str
    started_at: str
    ended_at: str
    duration: str

class _RunAttachment(TypedDict):
    id: str
    filename: str
    content_type: str
    size: int

class _RunLog(TypedDict, total=False):
    id: str
    timestamp: str
    level: str
    message: str
    source_file: str
    line_number: int

class _RunFileImportUpload(TypedDict):
    id: str
    name: str
    size: int
    content_type: str

class _RunFileImport(TypedDict):
    id: str
    upload: Optional[_RunFileImportUpload]

class _RunProcedureVersion(TypedDict):
    id: str
    value: str

class _RunOptional(TypedDict, total=False):
    ended_at: str
    created_by_user: Optional[_RunUser]
    created_by_station: Optional[_RunStation]
    procedure: Optional[_RunProcedure]
    unit: Optional[_RunUnit]
    phases: List[_RunPhase]
    procedure_version: Optional[_RunProcedureVersion]
    attachments: List[_RunAttachment]
    file_import: Optional[_RunFileImport]
    logs: List[_RunLog]

class Run(_RunOptional):
    id: str
    created_at: str
    started_at: str
    ended_at: str
    duration: str
    outcome: Outcome

class _SuccessResponseOptional(TypedDict, total=False):
    message: Optional[str]
    success: Literal[True]

class SuccessResponse(_SuccessResponseOptional):
    pass

class CreateRunResponse(SuccessResponse):
    id: str  # UUID format

class GetRunsResponse(SuccessResponse):
    result: List[Run]
# /TEMPORARY

@pytest.fixture(scope="class")
def client(api_key, tofupilot_server_url) -> TofuPilotClient:
    """Create a client configured for testing."""
    
    # Suppress banner for cleaner test output
    with patch("tofupilot.banner.print_banner_and_check_version"):
        
        # Create client pointing to localhost
        client = TofuPilotClient(
            api_key=api_key,
            url=tofupilot_server_url,
        )
        
        # Verify we're pointing to the right URL
        assert client._url == f"{tofupilot_server_url}/api/v1"
        
        return client
    
@pytest.fixture(scope="class")
def v2_client(api_key: str, tofupilot_server_url: str):
    """Create V2 client with proper credentials for unit validation."""
    return tofupilot.v2.TofuPilot(
        api_key=api_key,
        server_url=f"{tofupilot_server_url}/api",
    )

@pytest.fixture(scope="class")
def parentless_unit_serial_number_factory(api_key: str, tofupilot_server_url: str, procedure_id) -> Callable[[], str]:
    """Return a serial number for a unit which does not have a parent unit."""

    def create():
        from datetime import datetime, timezone, timedelta

        # TODO: Use v2 once it's released
        # For now we use v1 to be able to check the previous release
        client = TofuPilotClient(
            api_key=api_key,
            url=tofupilot_server_url,
        )
        
        """
        v2_client = tofupilot.v2.TofuPilot(
            api_key=api_key,
            server_url=f"{tofupilot_server_url}/api",
        )
        """

        # Generate unique serial numbers to avoid conflicts
        unique_id = str(uuid.uuid4())
        serial_number = f"SUB001_{unique_id}"
        
        # Create a simple run to establish the unit without a parent      
        client.create_run(
            unit_under_test={"serial_number": serial_number, "part_number": "One"},
            procedure_id=procedure_id,
            run_passed=True,
        )

        """
        start_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        end_time = datetime.now(timezone.utc) - timedelta(minutes=5)

        v2_client.runs.create(
            serial_number=serial_number,
            procedure_id=procedure_id,
            outcome="PASS",
            part_number="#1",
            started_at=start_time,
            ended_at=end_time,
        )
        """
        
        # Verify unit was created and has no parent
        """
        units_response = v2_client.units.list(serial_numbers=[serial_number])
        assert len(units_response.data) == 1, f"Unit {serial_number} was not created"
        
        unit = units_response.data[0]
        assert not hasattr(unit, 'parent_unit_id') or unit.parent_unit_id is None, f"Unit {serial_number} should not have a parent"
        """

        return serial_number
    
    return create

# Assertion helper methods

def assert_create_run_success(result):
    """Helper method to assert successful run creation response."""
    checkcast(CreateRunResponse, result)

def assert_get_runs_success(result):
    """Helper method to assert successful get_runs_by_serial_number response."""
    checkcast(GetRunsResponse, result)