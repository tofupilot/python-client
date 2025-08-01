"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import httpx
from tofupilot.v2.errors import TofuPilotError
from tofupilot.v2.models import procedure_createop as models_procedure_createop
from tofupilot.v2.types import BaseModel
from typing import List, Optional


class InternalServerErrorFailedToCreateProcedureErrorError500Data(BaseModel):
    message: str
    r"""The error message"""

    code: str
    r"""The error code"""

    issues: Optional[
        List[models_procedure_createop.ProcedureCreateInternalServerErrorIssue]
    ] = None
    r"""An array of issues that were responsible for the error"""


class InternalServerErrorFailedToCreateProcedureErrorError500(TofuPilotError):
    r"""The error information"""

    data: InternalServerErrorFailedToCreateProcedureErrorError500Data

    def __init__(
        self,
        data: InternalServerErrorFailedToCreateProcedureErrorError500Data,
        raw_response: httpx.Response,
        body: Optional[str] = None,
    ):
        fallback = body or raw_response.text
        message = str(data.message) or fallback
        super().__init__(message, raw_response, body)
        self.data = data


class ProcedureCreateProcedureNameIsRequiredError400Data(BaseModel):
    message: str
    r"""The error message"""

    code: str
    r"""The error code"""

    issues: Optional[List[models_procedure_createop.ProcedureCreateBadRequestIssue]] = (
        None
    )
    r"""An array of issues that were responsible for the error"""


class ProcedureCreateProcedureNameIsRequiredError400(TofuPilotError):
    r"""The error information"""

    data: ProcedureCreateProcedureNameIsRequiredError400Data

    def __init__(
        self,
        data: ProcedureCreateProcedureNameIsRequiredError400Data,
        raw_response: httpx.Response,
        body: Optional[str] = None,
    ):
        fallback = body or raw_response.text
        message = str(data.message) or fallback
        super().__init__(message, raw_response, body)
        self.data = data
