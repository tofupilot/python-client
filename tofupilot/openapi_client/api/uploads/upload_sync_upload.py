from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.failed_to_sync_upload_with_run_error_409 import FailedToSyncUploadWithRunError409
from ...models.internal_server_error_error_500 import InternalServerErrorError500
from ...models.unit_not_found_serial_number_error_404 import UnitNotFoundSerialNumberError404
from ...models.upload_sync_upload_body import UploadSyncUploadBody
from ...models.upload_sync_upload_response_200 import UploadSyncUploadResponse200
from ...types import Response


def _get_kwargs(
    *,
    body: UploadSyncUploadBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/uploads/sync",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        FailedToSyncUploadWithRunError409,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadSyncUploadResponse200,
    ]
]:
    if response.status_code == 200:
        response_200 = UploadSyncUploadResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = UnitNotFoundSerialNumberError404.from_dict(response.json())

        return response_404
    if response.status_code == 409:
        response_409 = FailedToSyncUploadWithRunError409.from_dict(response.json())

        return response_409
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
        FailedToSyncUploadWithRunError409,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadSyncUploadResponse200,
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
    body: UploadSyncUploadBody,
) -> Response[
    Union[
        FailedToSyncUploadWithRunError409,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadSyncUploadResponse200,
    ]
]:
    """Sync upload with run

     Updates upload metadata and links an upload to a run

    Args:
        body (UploadSyncUploadBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FailedToSyncUploadWithRunError409, InternalServerErrorError500, UnitNotFoundSerialNumberError404, UploadSyncUploadResponse200]]
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
    body: UploadSyncUploadBody,
) -> Optional[
    Union[
        FailedToSyncUploadWithRunError409,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadSyncUploadResponse200,
    ]
]:
    """Sync upload with run

     Updates upload metadata and links an upload to a run

    Args:
        body (UploadSyncUploadBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FailedToSyncUploadWithRunError409, InternalServerErrorError500, UnitNotFoundSerialNumberError404, UploadSyncUploadResponse200]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: UploadSyncUploadBody,
) -> Response[
    Union[
        FailedToSyncUploadWithRunError409,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadSyncUploadResponse200,
    ]
]:
    """Sync upload with run

     Updates upload metadata and links an upload to a run

    Args:
        body (UploadSyncUploadBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FailedToSyncUploadWithRunError409, InternalServerErrorError500, UnitNotFoundSerialNumberError404, UploadSyncUploadResponse200]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: UploadSyncUploadBody,
) -> Optional[
    Union[
        FailedToSyncUploadWithRunError409,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadSyncUploadResponse200,
    ]
]:
    """Sync upload with run

     Updates upload metadata and links an upload to a run

    Args:
        body (UploadSyncUploadBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FailedToSyncUploadWithRunError409, InternalServerErrorError500, UnitNotFoundSerialNumberError404, UploadSyncUploadResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
