from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.internal_server_error_error_500 import InternalServerErrorError500
from ...models.run_delete_single_response_200 import RunDeleteSingleResponse200
from ...models.unit_not_found_serial_number_error_404 import UnitNotFoundSerialNumberError404
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: UUID,
    *,
    test23: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_test23: Union[None, Unset, str]
    if isinstance(test23, Unset):
        json_test23 = UNSET
    else:
        json_test23 = test23
    params["test23"] = json_test23

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/v1/runs/{id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]]:
    if response.status_code == 200:
        response_200 = RunDeleteSingleResponse200.from_dict(response.json())

        return response_200
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
) -> Response[Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID,
    *,
    client: AuthenticatedClient,
    test23: Union[None, Unset, str] = UNSET,
) -> Response[Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]]:
    """Delete run

     Permanently removes a run identified by its ID

    Args:
        id (UUID): The ID of the run to delete
        test23 (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        id=id,
        test23=test23,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    *,
    client: AuthenticatedClient,
    test23: Union[None, Unset, str] = UNSET,
) -> Optional[Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]]:
    """Delete run

     Permanently removes a run identified by its ID

    Args:
        id (UUID): The ID of the run to delete
        test23 (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]
    """

    return sync_detailed(
        id=id,
        client=client,
        test23=test23,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    *,
    client: AuthenticatedClient,
    test23: Union[None, Unset, str] = UNSET,
) -> Response[Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]]:
    """Delete run

     Permanently removes a run identified by its ID

    Args:
        id (UUID): The ID of the run to delete
        test23 (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        id=id,
        test23=test23,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    *,
    client: AuthenticatedClient,
    test23: Union[None, Unset, str] = UNSET,
) -> Optional[Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]]:
    """Delete run

     Permanently removes a run identified by its ID

    Args:
        id (UUID): The ID of the run to delete
        test23 (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[InternalServerErrorError500, RunDeleteSingleResponse200, UnitNotFoundSerialNumberError404]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            test23=test23,
        )
    ).parsed
