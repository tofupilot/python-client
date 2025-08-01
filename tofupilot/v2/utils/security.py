"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

import base64

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .metadata import (
    SecurityMetadata,
    find_field_metadata,
)
import os


def get_security(security: Any) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    headers: Dict[str, str] = {}
    query_params: Dict[str, List[str]] = {}

    if security is None:
        return headers, query_params

    if not isinstance(security, BaseModel):
        raise TypeError("security must be a pydantic model")

    sec_fields: Dict[str, FieldInfo] = security.__class__.model_fields
    for name in sec_fields:
        sec_field = sec_fields[name]

        value = getattr(security, name)
        if value is None:
            continue

        metadata = find_field_metadata(sec_field, SecurityMetadata)
        if metadata is None:
            continue
        if metadata.option:
            _parse_security_option(headers, query_params, value)
            return headers, query_params
        if metadata.scheme:
            # Special case for basic auth or custom auth which could be a flattened model
            if metadata.sub_type in ["basic", "custom"] and not isinstance(
                value, BaseModel
            ):
                _parse_security_scheme(headers, query_params, metadata, name, security)
            else:
                _parse_security_scheme(headers, query_params, metadata, name, value)

    return headers, query_params


def get_security_from_env(security: Any, security_class: Any) -> Optional[BaseModel]:
    if security is not None:
        return security

    if not issubclass(security_class, BaseModel):
        raise TypeError("security_class must be a pydantic model class")

    security_dict: Any = {}

    if os.getenv("TOFUPILOT_API_KEY"):
        security_dict["api_key"] = os.getenv("TOFUPILOT_API_KEY")

    return security_class(**security_dict) if security_dict else None


def _parse_security_option(
    headers: Dict[str, str], query_params: Dict[str, List[str]], option: Any
):
    if not isinstance(option, BaseModel):
        raise TypeError("security option must be a pydantic model")

    opt_fields: Dict[str, FieldInfo] = option.__class__.model_fields
    for name in opt_fields:
        opt_field = opt_fields[name]

        metadata = find_field_metadata(opt_field, SecurityMetadata)
        if metadata is None or not metadata.scheme:
            continue
        _parse_security_scheme(
            headers, query_params, metadata, name, getattr(option, name)
        )


def _parse_security_scheme(
    headers: Dict[str, str],
    query_params: Dict[str, List[str]],
    scheme_metadata: SecurityMetadata,
    field_name: str,
    scheme: Any,
):
    scheme_type = scheme_metadata.scheme_type
    sub_type = scheme_metadata.sub_type

    if isinstance(scheme, BaseModel):
        if scheme_type == "http":
            if sub_type == "basic":
                _parse_basic_auth_scheme(headers, scheme)
                return
            if sub_type == "custom":
                return

        scheme_fields: Dict[str, FieldInfo] = scheme.__class__.model_fields
        for name in scheme_fields:
            scheme_field = scheme_fields[name]

            metadata = find_field_metadata(scheme_field, SecurityMetadata)
            if metadata is None or metadata.field_name is None:
                continue

            value = getattr(scheme, name)

            _parse_security_scheme_value(
                headers, query_params, scheme_metadata, metadata, name, value
            )
    else:
        _parse_security_scheme_value(
            headers, query_params, scheme_metadata, scheme_metadata, field_name, scheme
        )


def _parse_security_scheme_value(
    headers: Dict[str, str],
    query_params: Dict[str, List[str]],
    scheme_metadata: SecurityMetadata,
    security_metadata: SecurityMetadata,
    field_name: str,
    value: Any,
):
    scheme_type = scheme_metadata.scheme_type
    sub_type = scheme_metadata.sub_type

    header_name = security_metadata.get_field_name(field_name)

    if scheme_type == "apiKey":
        if sub_type == "header":
            headers[header_name] = value
        elif sub_type == "query":
            query_params[header_name] = [value]
        else:
            raise ValueError("sub type {sub_type} not supported")
    elif scheme_type == "openIdConnect":
        headers[header_name] = _apply_bearer(value)
    elif scheme_type == "oauth2":
        if sub_type != "client_credentials":
            headers[header_name] = _apply_bearer(value)
    elif scheme_type == "http":
        if sub_type == "bearer":
            headers[header_name] = _apply_bearer(value)
        elif sub_type == "custom":
            return
        else:
            raise ValueError("sub type {sub_type} not supported")
    else:
        raise ValueError("scheme type {scheme_type} not supported")


def _apply_bearer(token: str) -> str:
    return token.lower().startswith("bearer ") and token or f"Bearer {token}"


def _parse_basic_auth_scheme(headers: Dict[str, str], scheme: Any):
    username = ""
    password = ""

    if not isinstance(scheme, BaseModel):
        raise TypeError("basic auth scheme must be a pydantic model")

    scheme_fields: Dict[str, FieldInfo] = scheme.__class__.model_fields
    for name in scheme_fields:
        scheme_field = scheme_fields[name]

        metadata = find_field_metadata(scheme_field, SecurityMetadata)
        if metadata is None or metadata.field_name is None:
            continue

        field_name = metadata.field_name
        value = getattr(scheme, name)

        if field_name == "username":
            username = value
        if field_name == "password":
            password = value

    data = f"{username}:{password}".encode()
    headers["Authorization"] = f"Basic {base64.b64encode(data).decode()}"
