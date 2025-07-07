"""Type definitions for TofuPilot API responses."""

from typing import Dict, List, Optional, TypedDict, Union, Any, Literal

from .models import RunOutcome, LogLevel

# Type aliases for commonly used literal types
PhaseOutcome = Literal["PASS", "FAIL", "SKIP", "ERROR"]
MeasurementOutcome = Literal["PASS", "FAIL", "UNSET"]
QoSLevel = Literal[0, 1, 2]
GetRunsSortOption = Literal["-startedAt", "startedAt", "-createdAt", "createdAt", "-duration", "duration"]
GetUnitsSortOption = Literal["-serialNumber", "serialNumber", "-createdAt", "createdAt"]
GetRunsExcludeField = Literal["createdBy", "procedure", "unit", "phases", "procedureVersion", "attachments", "measurements", "logs", "all"]
GetUnitsExcludeField = Literal["all", "batch", "parent", "createdFrom", "revision", "parentChanges", "children", "runs", "createdBy"]
ImporterType = Literal["OPENHTF"]

class CreatedByUser(TypedDict):
    id: str  # UUID format
    name: Optional[str]

class CreatedByStation(TypedDict):
    id: str  # UUID format
    name: str

class _BatchOptional(TypedDict, total=False):
    id: str  # UUID format

class Batch(_BatchOptional):
    number: str

class _ComponentOptional(TypedDict, total=False):
    id: str  # UUID format

class Component(_ComponentOptional):
    partNumber: str
    name: str

class Image(TypedDict):
    s3Key: str

class Revision(TypedDict):
    id: str  # UUID format
    identifier: str
    component: Optional[Component]
    image: Optional[Image]

class Procedure(TypedDict):
    id: str  # UUID format
    name: str
    identifier: str

class ProcedureVersion(TypedDict):
    id: str  # UUID format
    value: str

class _DataSeriesOptional(TypedDict, total=False):
    units: Optional[str]

class DataSeries(_DataSeriesOptional):
    data: List[float]

class _MeasurementOptional(TypedDict, total=False):
    units: Optional[str]
    validators: Optional[List[str]]
    lowerLimit: Optional[float]
    upperLimit: Optional[float]
    jsonValue: Optional[Any]

class Measurement(_MeasurementOptional):
    id: str  # UUID format
    name: str
    outcome: MeasurementOutcome
    value: Optional[float]
    stringValue: Optional[str]
    boolValue: Optional[bool]
    dataSeries: Optional[List[DataSeries]]

class SumarisedPhase(TypedDict):
    id: str  # UUID format
    name: str
    outcome: PhaseOutcome

class _PhaseOptional(TypedDict, total=False):
    docstring: Optional[str]
    measurements: List[Measurement]

class Phase(_PhaseOptional):
    id: str  # UUID format
    name: str
    outcome: PhaseOutcome
    startedAt: str  # ISO date-time format
    duration: str  # duration format

class _SummarisedUnitOptional(TypedDict, total=False):
    batch: Optional[Batch]

class SummarisedUnit(_SummarisedUnitOptional):
    id: str  # UUID format
    serialNumber: str
    revision: Revision

class Attachment(TypedDict):
    id: str  # UUID format
    name: str

class _RunOptional(TypedDict, total=False):
    createdByUser: Optional[CreatedByUser]
    createdByStation: Optional[CreatedByStation]
    procedure: Optional[Procedure]
    unit: Optional[SummarisedUnit]
    phases: List[Phase]
    procedureVersion: Optional[ProcedureVersion]
    attachments: List[Attachment]

class Run(_RunOptional):
    id: str  # UUID format
    outcome: RunOutcome
    startedAt: str  # ISO date-time format
    createdAt: str  # ISO date-time format
    duration: str   # duration format

class _UnitRunOptional(TypedDict, total=False):
    duration: str # duration format

class UnitRun(_UnitRunOptional): # Not done, since get_units.parent.runs was removed
    id: str  # UUID format
    startedAt: str  # ISO date-time format
    createdAt: str  # ISO date-time format
    outcome: RunOutcome
    phases: List[SumarisedPhase]
    procedure: Optional[Procedure]

class UnitRevision(TypedDict):
    identifier: str
    component: Optional[Component]
    image: Optional[Image]

class UnitParent(TypedDict):
    id: str  # UUID format
    serialNumber: str
    nbOfChildren: int
    revision: UnitRevision
    # runs: List[UnitRun] # Removed by manon

class UnitChild(TypedDict):
    id: str  # UUID format
    serialNumber: str
    nbOfChildren: int
    revision: UnitRevision

class _UnitCreatedFromOptional(TypedDict, total=False):
    duration: str # duration format

class UnitCreatedFrom(_UnitCreatedFromOptional):
    id: str  # UUID format
    createdAt: str  # ISO date-time format
    startedAt: str  # ISO date-time format
    outcome: RunOutcome
    phases: List[SumarisedPhase]
    procedure: Optional[Procedure]

class SummarizedUnit(TypedDict):
    id: str # UUID format
    serialNumber: str

class UnitRevisionFull(TypedDict):
    id: str  # UUID format
    identifier: str
    component: Optional[Component]
    units: List[SummarizedUnit]  # List of {"id": UUID, "serialNumber": string}

class ParentChangeAction(TypedDict):
    id: str  # UUID format
    procedure: Procedure

class ParentChangeUnitComponent(TypedDict):
    id: str  # UUID format
    name: str

class ParentChangeUnitRevision(TypedDict):
    id: str  # UUID format
    identifier: str
    image: Optional[Image]
    component: ParentChangeUnitComponent

class ParentChangeUnit(TypedDict):
    id: str # UUID format
    serialNumber: str
    revision: ParentChangeUnitRevision  # Complex nested structure

class _ParentChangeOptional(TypedDict, total=False):
    actor: Union[CreatedByStation, CreatedByUser] # TODO: Make union of relevant thing

class ParentChange(_ParentChangeOptional):
    createdAt: str  # ISO date-time format
    action: ParentChangeAction
    unit: ParentChangeUnit
    old: Optional[SummarizedUnit]
    new: Optional[SummarizedUnit]

class _UnitOptional(TypedDict, total=False):
    createdByUser: Optional[CreatedByUser]
    createdByStation: Optional[CreatedByStation]
    batch: Optional[Batch]
    parent: Optional[UnitParent]
    children: Optional[List[UnitChild]]
    createdFrom: Optional[UnitCreatedFrom]
    revision: Optional[UnitRevisionFull]
    runs: List[UnitRun]

class Unit(_UnitOptional):
    id: str  # UUID format
    serialNumber: str
    createdAt: str  # ISO date-time format
    parentChanges: List[ParentChange]

class Meta(TypedDict):
    total: int
    limit: Optional[int]
    offset: int

class _SuccessResponseOptional(TypedDict, total=False):
    message: Optional[str]
    warnings: object # TODO: strip, or remove from output

class SuccessResponse(_SuccessResponseOptional):
    pass

class GetRunsResponse(SuccessResponse):
    data: List[Run]
    meta: Meta

class GetUnitsResponse(SuccessResponse):
    data: List[Unit]
    meta: Meta

class CreateRunResponse(SuccessResponse):
    id: str  # UUID format

class DeleteRunResponse(SuccessResponse):
    pass  # Empty object response

class _ClientOptions(TypedDict):
    transport: str
    protocol: int
    reconnect_on_failure: bool


class _WillOptionsOptional(TypedDict, total=False):
    qos: QoSLevel
    retain: bool

class _WillOptions(_WillOptionsOptional):
    topic: str
    payload: str


class _ConnectOptions(TypedDict):
    host: str
    port: int
    keepalive: int


class _PublishOptionsOptional(TypedDict, total=False):
    retain: bool
    qos: QoSLevel

class _PublishOptions(_PublishOptionsOptional):
    topic: str


class _SubscribeOptionsOptional(TypedDict, total=False):
    qos: QoSLevel

class _SubscribeOptions(_SubscribeOptionsOptional):
    topic: str


class _StreamingCredentials(TypedDict):
    token: str
    operatorPage: str
    clientOptions: _ClientOptions
    willOptions: _WillOptions
    connectOptions: _ConnectOptions
    publishOptions: _PublishOptions
    subscribeOptions: _SubscribeOptions


class _InitializeUploadResponse(TypedDict):
    id: str  # UUID format
    uploadUrl: str


class _OpenHTFImportResultOptional(TypedDict, total=False):
    run_id: str
    upload_id: str
    error: Dict[str, str]

class _OpenHTFImportResult(_OpenHTFImportResultOptional):
    success: Literal[True]


class _StreamingResultOptional(TypedDict, total=False):
    values: _StreamingCredentials
    error: Dict[str, Any]

class _StreamingResult(_StreamingResultOptional):
    success: bool

_UpdateUnitResponse = Dict[str, str]  # Used by _update_unit()
_DeleteUnitResponse = Dict[str, str]  # Used by _delete_unit()
