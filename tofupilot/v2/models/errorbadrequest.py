"""TofuPilot SDK Runtime. DO NOT EDIT — maintained in clients/generator/runtime/."""

from __future__ import annotations
from tofupilot.v2.types import BaseModel
from typing_extensions import TypedDict


class ErrorBADREQUESTIssueTypedDict(TypedDict):
    message: str


class ErrorBADREQUESTIssue(BaseModel):
    message: str
