from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.circular_parent_relationship_not_allowed_sub_units_not_found_error_400 import (
    CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
)
from ...models.internal_server_error_error_500 import InternalServerErrorError500
from ...models.run_create_from_file_body import RunCreateFromFileBody
from ...models.run_create_from_file_response_200 import RunCreateFromFileResponse200
from ...models.unit_not_found_serial_number_error_404 import UnitNotFoundSerialNumberError404
from ...types import Response


def _get_kwargs(
    *,
    body: RunCreateFromFileBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/import",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunCreateFromFileResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    if response.status_code == 200:
        response_200 = RunCreateFromFileResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = CircularParentRelationshipNotAllowedSubUnitsNotFoundError400.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = UnitNotFoundSerialNumberError404.from_dict(response.json())

        return response_404
    if response.status_code == 500:
        response_500 = InternalServerErrorError500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunCreateFromFileResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: RunCreateFromFileBody,
) -> Response[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunCreateFromFileResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Import log file

     Processes an uploaded log file to create a run

    Args:
        body (RunCreateFromFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, RunCreateFromFileResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: RunCreateFromFileBody,
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunCreateFromFileResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Import log file

     Processes an uploaded log file to create a run

    Args:
        body (RunCreateFromFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, RunCreateFromFileResponse200, UnitNotFoundSerialNumberError404]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: RunCreateFromFileBody,
) -> Response[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunCreateFromFileResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Import log file

     Processes an uploaded log file to create a run

    Args:
        body (RunCreateFromFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, RunCreateFromFileResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: RunCreateFromFileBody,
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunCreateFromFileResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Import log file

     Processes an uploaded log file to create a run

    Args:
        body (RunCreateFromFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, RunCreateFromFileResponse200, UnitNotFoundSerialNumberError404]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
