"""
Shared test utilities for TofuPilot Python client tests.
"""

import pytest
import uuid
from unittest.mock import patch
from typing import Callable, TypedDict, Optional, Literal, List, Dict, Any

import tofupilot
from tofupilot import TofuPilotClient
import tofupilot.v2

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

# V2 client fixture for validation
@pytest.fixture(scope="class")
def v2_client(api_key, tofupilot_server_url) -> tofupilot.v2.TofuPilot:
    """Create a v2 client for validating v1 created runs."""
    return tofupilot.v2.TofuPilot(
        api_key=api_key,
        server_url=f"{tofupilot_server_url}/api",
    )

# Assertion helper methods

def assert_create_run_success(result):
    """Helper method to assert successful run creation response."""
    checkcast(CreateRunResponse, result)

def assert_get_runs_success(result):
    """Helper method to assert successful get_runs_by_serial_number response."""
    checkcast(GetRunsResponse, result)

def validate_v1_run_creation(v2_client, run_id: str, expected_fields: Dict[str, Any]):
    """
    Validate that a run created via v1 API has the expected field values.
    Uses v2 client to fetch and verify the run.
    
    Args:
        v2_client: The v2 TofuPilot client
        run_id: The ID of the created run
        expected_fields: Dictionary of expected field values
            - serial_number
            - part_number
            - part_name
            - revision
            - batch_number
            - outcome
            - procedure_version
    """
    # Fetch the run using v2 client
    run = v2_client.runs.get(id=run_id)
    assert run.id == run_id, f"Run ID mismatch: {run.id} != {run_id}"
    
    # Validate unit fields
    if "serial_number" in expected_fields:
        assert run.unit.serial_number == expected_fields["serial_number"], \
            f"Serial number mismatch: {run.unit.serial_number} != {expected_fields['serial_number']}"
    
    if "part_number" in expected_fields:
        assert run.unit.part.number == expected_fields["part_number"], \
            f"Part number mismatch: {run.unit.part.number} != {expected_fields['part_number']}"
    
    # Note: part_name is deprecated in v1 API and will use default value
    if "part_name" in expected_fields:
        # Skip validation for deprecated field
        pass
    
    if "revision" in expected_fields:
        # In v2 API, revision is under unit.part.revision
        assert run.unit.part.revision.number == expected_fields["revision"], \
            f"Revision mismatch: {run.unit.part.revision.number} != {expected_fields['revision']}"
    
    if "batch_number" in expected_fields and expected_fields["batch_number"]:
        assert run.unit.batch is not None, "Batch should exist"
        assert run.unit.batch.number == expected_fields["batch_number"], \
            f"Batch number mismatch: {run.unit.batch.number} != {expected_fields['batch_number']}"
    
    # Validate run fields
    if "outcome" in expected_fields:
        # Convert boolean run_passed to outcome string
        if isinstance(expected_fields["outcome"], bool):
            expected_outcome = "PASS" if expected_fields["outcome"] else "FAIL"
        else:
            expected_outcome = expected_fields["outcome"]
        assert run.outcome == expected_outcome, \
            f"Outcome mismatch: {run.outcome} != {expected_outcome}"
    
    if "procedure_version" in expected_fields and expected_fields["procedure_version"]:
        # In v2, procedure version is an object with 'tag' field
        if hasattr(run, 'procedure') and hasattr(run.procedure, 'version'):
            assert run.procedure.version.tag == expected_fields["procedure_version"], \
                f"Procedure version mismatch: {run.procedure.version.tag} != {expected_fields['procedure_version']}"
    
    return run