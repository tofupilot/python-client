"""Type definitions for TofuPilot API responses."""

from typing import Dict, List, Optional, TypedDict, Union, Any, Literal

QoSLevel = Literal[0, 1, 2]

class _SuccessResponseOptional(TypedDict, total=False):
    message: Optional[str]

class SuccessResponse(_SuccessResponseOptional):
    success: Literal[True]

class CreateRunResponse(SuccessResponse):
    id: str  # UUID format

class GetRunsBySerialNumberResponse(SuccessResponse):
    runs: List[Dict[str, Any]]  # Array of run objects returned by V1 API

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