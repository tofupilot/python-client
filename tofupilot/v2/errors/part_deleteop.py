"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import httpx
from tofupilot.v2.errors import TofuPilotError
from tofupilot.v2.models import part_deleteop as models_part_deleteop
from tofupilot.v2.types import BaseModel
from typing import List, Optional


class PartDeleteInternalServerErrorError500Data(BaseModel):
    message: str
    r"""The error message"""

    code: str
    r"""The error code"""

    issues: Optional[List[models_part_deleteop.PartDeleteInternalServerErrorIssue]] = (
        None
    )
    r"""An array of issues that were responsible for the error"""


class PartDeleteInternalServerErrorError500(TofuPilotError):
    r"""The error information"""

    data: PartDeleteInternalServerErrorError500Data

    def __init__(
        self,
        data: PartDeleteInternalServerErrorError500Data,
        raw_response: httpx.Response,
        body: Optional[str] = None,
    ):
        fallback = body or raw_response.text
        message = str(data.message) or fallback
        super().__init__(message, raw_response, body)
        self.data = data


class PartWithNumberNumberNotFoundError404Data(BaseModel):
    message: str
    r"""The error message"""

    code: str
    r"""The error code"""

    issues: Optional[List[models_part_deleteop.PartDeleteNotFoundIssue]] = None
    r"""An array of issues that were responsible for the error"""


class PartWithNumberNumberNotFoundError404(TofuPilotError):
    r"""The error information"""

    data: PartWithNumberNumberNotFoundError404Data

    def __init__(
        self,
        data: PartWithNumberNumberNotFoundError404Data,
        raw_response: httpx.Response,
        body: Optional[str] = None,
    ):
        fallback = body or raw_response.text
        message = str(data.message) or fallback
        super().__init__(message, raw_response, body)
        self.data = data
