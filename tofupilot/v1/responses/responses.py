"""Type definitions for TofuPilot API responses."""

from typing import Dict, List, Optional, TypedDict, Union, Any, Literal

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

class SuccessResponse(_SuccessResponseOptional):
    success: Literal[True]

class CreateRunResponse(SuccessResponse):
    id: str  # UUID format

class GetRunsResponse(SuccessResponse):
    result: List[Run]

class _InitializeUploadResponse(TypedDict):
    id: str  # UUID format
    uploadUrl: str


class _OpenHTFImportResultOptional(TypedDict, total=False):
    run_id: str
    upload_id: str
    error: Dict[str, str]

class _OpenHTFImportResult(_OpenHTFImportResultOptional):
    success: Literal[True]


# Error response types based on network utility functions
class ErrorDetail(TypedDict):
    message: str


class BaseErrorResponse(TypedDict):
    success: Literal[False]
    message: None
    error: ErrorDetail


class HttpErrorResponse(BaseErrorResponse):
    """Error response from HTTP errors (handle_http_error)"""
    warnings: Optional[List[str]]
    status_code: int


class NetworkErrorResponse(BaseErrorResponse):
    """Error response from network errors (handle_network_error)"""
    warnings: None
    status_code: None


# Union type for all possible error responses
ErrorResponse = Union[HttpErrorResponse, NetworkErrorResponse] 