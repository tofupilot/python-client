from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.internal_server_error_error_500 import InternalServerErrorError500
from ...models.unit_delete_response_200 import UnitDeleteResponse200
from ...models.unit_not_found_serial_number_error_404 import UnitNotFoundSerialNumberError404
from ...types import Response


def _get_kwargs(
    serial_number: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/v1/units/{serial_number}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]]:
    if response.status_code == 200:
        response_200 = UnitDeleteResponse200.from_dict(response.json())

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
) -> Response[Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    serial_number: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]]:
    """Delete unit

     Permanently removes a unit identified by its serial number

    Args:
        serial_number (str): The serial number of the unit

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        serial_number=serial_number,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    serial_number: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]]:
    """Delete unit

     Permanently removes a unit identified by its serial number

    Args:
        serial_number (str): The serial number of the unit

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]
    """

    return sync_detailed(
        serial_number=serial_number,
        client=client,
    ).parsed


async def asyncio_detailed(
    serial_number: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]]:
    """Delete unit

     Permanently removes a unit identified by its serial number

    Args:
        serial_number (str): The serial number of the unit

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        serial_number=serial_number,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    serial_number: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]]:
    """Delete unit

     Permanently removes a unit identified by its serial number

    Args:
        serial_number (str): The serial number of the unit

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[InternalServerErrorError500, UnitDeleteResponse200, UnitNotFoundSerialNumberError404]
    """

    return (
        await asyncio_detailed(
            serial_number=serial_number,
            client=client,
        )
    ).parsed
