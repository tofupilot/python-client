"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from tofupilot.v2.types import BaseModel
from typing_extensions import TypedDict


class ProcedureCreateRequestTypedDict(TypedDict):
    name: str
    r"""Name of the procedure. Must be unique within the organization."""


class ProcedureCreateRequest(BaseModel):
    name: str
    r"""Name of the procedure. Must be unique within the organization."""


class ProcedureCreateInternalServerErrorIssueTypedDict(TypedDict):
    message: str


class ProcedureCreateInternalServerErrorIssue(BaseModel):
    message: str


class ProcedureCreateBadRequestIssueTypedDict(TypedDict):
    message: str


class ProcedureCreateBadRequestIssue(BaseModel):
    message: str


class ProcedureCreateResponseTypedDict(TypedDict):
    r"""Procedure created successfully"""

    id: str
    r"""Unique identifier for the created procedure."""


class ProcedureCreateResponse(BaseModel):
    r"""Procedure created successfully"""

    id: str
    r"""Unique identifier for the created procedure."""
