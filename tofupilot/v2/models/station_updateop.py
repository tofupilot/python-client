"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from tofupilot.v2.types import BaseModel
from tofupilot.v2.utils import FieldMetadata, PathParamMetadata, RequestMetadata
from typing import Literal, Optional, Union
from typing_extensions import Annotated, NotRequired, TypeAliasType, TypedDict


StationUpdateImageIDEnum = Literal[""]

StationUpdateImageIDUnionTypedDict = TypeAliasType(
    "StationUpdateImageIDUnionTypedDict", Union[str, StationUpdateImageIDEnum]
)
r"""Upload ID for the station image, or empty string to remove image"""


StationUpdateImageIDUnion = TypeAliasType(
    "StationUpdateImageIDUnion", Union[str, StationUpdateImageIDEnum]
)
r"""Upload ID for the station image, or empty string to remove image"""


class StationUpdateRequestBodyTypedDict(TypedDict):
    name: NotRequired[str]
    r"""New name for the station"""
    identifier: NotRequired[str]
    r"""New identifier for the station"""
    image_id: NotRequired[StationUpdateImageIDUnionTypedDict]
    r"""Upload ID for the station image, or empty string to remove image"""


class StationUpdateRequestBody(BaseModel):
    name: Optional[str] = None
    r"""New name for the station"""

    identifier: Optional[str] = None
    r"""New identifier for the station"""

    image_id: Optional[StationUpdateImageIDUnion] = None
    r"""Upload ID for the station image, or empty string to remove image"""


class StationUpdateRequestTypedDict(TypedDict):
    id: str
    r"""Unique identifier of the station to update"""
    request_body: StationUpdateRequestBodyTypedDict


class StationUpdateRequest(BaseModel):
    id: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]
    r"""Unique identifier of the station to update"""

    request_body: Annotated[
        StationUpdateRequestBody,
        FieldMetadata(request=RequestMetadata(media_type="application/json")),
    ]


class StationUpdateInternalServerErrorIssueTypedDict(TypedDict):
    message: str


class StationUpdateInternalServerErrorIssue(BaseModel):
    message: str


class StationUpdateConflictIssueTypedDict(TypedDict):
    message: str


class StationUpdateConflictIssue(BaseModel):
    message: str


class StationUpdateNotFoundIssueTypedDict(TypedDict):
    message: str


class StationUpdateNotFoundIssue(BaseModel):
    message: str


class StationUpdateResponseTypedDict(TypedDict):
    r"""Station updated successfully"""

    id: str
    r"""Unique identifier of the updated station"""
    identifier: str
    r"""Station identifier"""
    name: str
    r"""Name of the station"""


class StationUpdateResponse(BaseModel):
    r"""Station updated successfully"""

    id: str
    r"""Unique identifier of the updated station"""

    identifier: str
    r"""Station identifier"""

    name: str
    r"""Name of the station"""
