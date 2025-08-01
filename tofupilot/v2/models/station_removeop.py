"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from tofupilot.v2.types import BaseModel
from tofupilot.v2.utils import FieldMetadata, PathParamMetadata
from typing_extensions import Annotated, TypedDict


class StationRemoveRequestTypedDict(TypedDict):
    id: str
    r"""Unique identifier of the station to remove"""


class StationRemoveRequest(BaseModel):
    id: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]
    r"""Unique identifier of the station to remove"""


class StationRemoveInternalServerErrorIssueTypedDict(TypedDict):
    message: str


class StationRemoveInternalServerErrorIssue(BaseModel):
    message: str


class StationRemoveNotFoundIssueTypedDict(TypedDict):
    message: str


class StationRemoveNotFoundIssue(BaseModel):
    message: str


class StationRemoveBadRequestIssueTypedDict(TypedDict):
    message: str


class StationRemoveBadRequestIssue(BaseModel):
    message: str


class StationRemoveResponseTypedDict(TypedDict):
    r"""Station removed successfully"""

    id: str
    r"""Unique identifier of the removed station"""


class StationRemoveResponse(BaseModel):
    r"""Station removed successfully"""

    id: str
    r"""Unique identifier of the removed station"""
