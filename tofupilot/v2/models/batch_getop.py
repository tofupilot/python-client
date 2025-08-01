"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from datetime import datetime
from pydantic import model_serializer
from tofupilot.v2.types import (
    BaseModel,
    Nullable,
    OptionalNullable,
    UNSET,
    UNSET_SENTINEL,
)
from tofupilot.v2.utils import FieldMetadata, PathParamMetadata
from typing import List
from typing_extensions import Annotated, NotRequired, TypedDict


class BatchGetRequestTypedDict(TypedDict):
    number: str
    r"""Number of the batch to retrieve."""


class BatchGetRequest(BaseModel):
    number: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]
    r"""Number of the batch to retrieve."""


class BatchGetInternalServerErrorIssueTypedDict(TypedDict):
    message: str


class BatchGetInternalServerErrorIssue(BaseModel):
    message: str


class BatchGetNotFoundIssueTypedDict(TypedDict):
    message: str


class BatchGetNotFoundIssue(BaseModel):
    message: str


class BatchGetCreatedByUserTypedDict(TypedDict):
    r"""User who created this batch."""

    id: str
    r"""User ID."""
    name: Nullable[str]
    r"""User display name."""
    image: Nullable[str]
    r"""User profile image URL."""


class BatchGetCreatedByUser(BaseModel):
    r"""User who created this batch."""

    id: str
    r"""User ID."""

    name: Nullable[str]
    r"""User display name."""

    image: Nullable[str]
    r"""User profile image URL."""

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = []
        nullable_fields = ["name", "image"]
        null_default_fields = []

        serialized = handler(self)

        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias or n
            val = serialized.get(k)
            serialized.pop(k, None)

            optional_nullable = k in optional_fields and k in nullable_fields
            is_set = (
                self.__pydantic_fields_set__.intersection({n})
                or k in null_default_fields
            )  # pylint: disable=no-member

            if val is not None and val != UNSET_SENTINEL:
                m[k] = val
            elif val != UNSET_SENTINEL and (
                not k in optional_fields or (optional_nullable and is_set)
            ):
                m[k] = val

        return m


class BatchGetCreatedByStationTypedDict(TypedDict):
    r"""Station that created this batch."""

    id: str
    r"""Station ID."""
    name: str
    r"""Station name."""
    image: Nullable[str]
    r"""Station image URL."""


class BatchGetCreatedByStation(BaseModel):
    r"""Station that created this batch."""

    id: str
    r"""Station ID."""

    name: str
    r"""Station name."""

    image: Nullable[str]
    r"""Station image URL."""

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = []
        nullable_fields = ["image"]
        null_default_fields = []

        serialized = handler(self)

        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias or n
            val = serialized.get(k)
            serialized.pop(k, None)

            optional_nullable = k in optional_fields and k in nullable_fields
            is_set = (
                self.__pydantic_fields_set__.intersection({n})
                or k in null_default_fields
            )  # pylint: disable=no-member

            if val is not None and val != UNSET_SENTINEL:
                m[k] = val
            elif val != UNSET_SENTINEL and (
                not k in optional_fields or (optional_nullable and is_set)
            ):
                m[k] = val

        return m


class BatchGetRevisionTypedDict(TypedDict):
    r"""Revision information for this unit."""

    id: str
    r"""Revision ID."""
    number: str
    r"""Revision number."""
    image: Nullable[str]
    r"""Revision image URL."""


class BatchGetRevision(BaseModel):
    r"""Revision information for this unit."""

    id: str
    r"""Revision ID."""

    number: str
    r"""Revision number."""

    image: Nullable[str]
    r"""Revision image URL."""

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = []
        nullable_fields = ["image"]
        null_default_fields = []

        serialized = handler(self)

        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias or n
            val = serialized.get(k)
            serialized.pop(k, None)

            optional_nullable = k in optional_fields and k in nullable_fields
            is_set = (
                self.__pydantic_fields_set__.intersection({n})
                or k in null_default_fields
            )  # pylint: disable=no-member

            if val is not None and val != UNSET_SENTINEL:
                m[k] = val
            elif val != UNSET_SENTINEL and (
                not k in optional_fields or (optional_nullable and is_set)
            ):
                m[k] = val

        return m


class BatchGetPartTypedDict(TypedDict):
    r"""Part information with revision details for this unit."""

    id: str
    r"""Part ID."""
    number: str
    r"""Part number."""
    name: str
    r"""Part name."""
    revision: BatchGetRevisionTypedDict
    r"""Revision information for this unit."""


class BatchGetPart(BaseModel):
    r"""Part information with revision details for this unit."""

    id: str
    r"""Part ID."""

    number: str
    r"""Part number."""

    name: str
    r"""Part name."""

    revision: BatchGetRevision
    r"""Revision information for this unit."""


class BatchGetUnitTypedDict(TypedDict):
    id: str
    r"""Unit ID."""
    serial_number: str
    r"""Unit serial number."""
    created_at: datetime
    r"""ISO 8601 timestamp when the unit was created."""
    part: BatchGetPartTypedDict
    r"""Part information with revision details for this unit."""


class BatchGetUnit(BaseModel):
    id: str
    r"""Unit ID."""

    serial_number: str
    r"""Unit serial number."""

    created_at: datetime
    r"""ISO 8601 timestamp when the unit was created."""

    part: BatchGetPart
    r"""Part information with revision details for this unit."""


class BatchGetResponseTypedDict(TypedDict):
    r"""Batch retrieved successfully"""

    id: str
    r"""Unique identifier for the batch."""
    number: str
    r"""Batch number."""
    created_at: datetime
    r"""ISO 8601 timestamp when the batch was created."""
    units: List[BatchGetUnitTypedDict]
    r"""Array of units in this batch. Empty array if no units."""
    created_by_user: NotRequired[Nullable[BatchGetCreatedByUserTypedDict]]
    r"""User who created this batch."""
    created_by_station: NotRequired[Nullable[BatchGetCreatedByStationTypedDict]]
    r"""Station that created this batch."""


class BatchGetResponse(BaseModel):
    r"""Batch retrieved successfully"""

    id: str
    r"""Unique identifier for the batch."""

    number: str
    r"""Batch number."""

    created_at: datetime
    r"""ISO 8601 timestamp when the batch was created."""

    units: List[BatchGetUnit]
    r"""Array of units in this batch. Empty array if no units."""

    created_by_user: OptionalNullable[BatchGetCreatedByUser] = UNSET
    r"""User who created this batch."""

    created_by_station: OptionalNullable[BatchGetCreatedByStation] = UNSET
    r"""Station that created this batch."""

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = ["created_by_user", "created_by_station"]
        nullable_fields = ["created_by_user", "created_by_station"]
        null_default_fields = []

        serialized = handler(self)

        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias or n
            val = serialized.get(k)
            serialized.pop(k, None)

            optional_nullable = k in optional_fields and k in nullable_fields
            is_set = (
                self.__pydantic_fields_set__.intersection({n})
                or k in null_default_fields
            )  # pylint: disable=no-member

            if val is not None and val != UNSET_SENTINEL:
                m[k] = val
            elif val != UNSET_SENTINEL and (
                not k in optional_fields or (optional_nullable and is_set)
            ):
                m[k] = val

        return m
