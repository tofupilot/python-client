"""TofuPilot SDK Runtime. DO NOT EDIT — maintained in clients/generator/runtime/."""

from __future__ import annotations
from tofupilot.v2.types import BaseModel
from typing_extensions import TypedDict


class ErrorBADGATEWAYIssueTypedDict(TypedDict):
    message: str


class ErrorBADGATEWAYIssue(BaseModel):
    message: str
