"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import httpx
from tofupilot.v2.errors import TofuPilotError
from tofupilot.v2.models import batch_deleteop as models_batch_deleteop
from tofupilot.v2.types import BaseModel
from typing import List, Optional


class BatchDeleteInternalServerErrorError500Data(BaseModel):
    message: str
    r"""The error message"""

    code: str
    r"""The error code"""

    issues: Optional[
        List[models_batch_deleteop.BatchDeleteInternalServerErrorIssue]
    ] = None
    r"""An array of issues that were responsible for the error"""


class BatchDeleteInternalServerErrorError500(TofuPilotError):
    r"""The error information"""

    data: BatchDeleteInternalServerErrorError500Data

    def __init__(
        self,
        data: BatchDeleteInternalServerErrorError500Data,
        raw_response: httpx.Response,
        body: Optional[str] = None,
    ):
        fallback = body or raw_response.text
        message = str(data.message) or fallback
        super().__init__(message, raw_response, body)
        self.data = data


class BatchWithIDBatchIDNotFoundError404Data(BaseModel):
    message: str
    r"""The error message"""

    code: str
    r"""The error code"""

    issues: Optional[List[models_batch_deleteop.BatchDeleteNotFoundIssue]] = None
    r"""An array of issues that were responsible for the error"""


class BatchWithIDBatchIDNotFoundError404(TofuPilotError):
    r"""The error information"""

    data: BatchWithIDBatchIDNotFoundError404Data

    def __init__(
        self,
        data: BatchWithIDBatchIDNotFoundError404Data,
        raw_response: httpx.Response,
        body: Optional[str] = None,
    ):
        fallback = body or raw_response.text
        message = str(data.message) or fallback
        super().__init__(message, raw_response, body)
        self.data = data
