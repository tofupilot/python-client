from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.internal_server_error_error_500 import InternalServerErrorError500
from ...models.invalid_api_key_please_verify_your_key_and_try_again_error_401 import (
    InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
)
from ...models.you_must_belong_to_an_organization_to_upload_a_file_error_403 import (
    YouMustBelongToAnOrganizationToUploadAFileError403,
)
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/rooms",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        None,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    if response.status_code == 200:
        response_200 = cast(None, response.json())
        return response_200
    if response.status_code == 401:
        response_401 = InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = YouMustBelongToAnOrganizationToUploadAFileError403.from_dict(response.json())

        return response_403
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
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        None,
        YouMustBelongToAnOrganizationToUploadAFileError403,
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
) -> Response[
    Union[
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        None,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    """OUTDATED

     This endpoint only exists so that some old clients do not throw an error

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[InternalServerErrorError500, InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401, None, YouMustBelongToAnOrganizationToUploadAFileError403]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        None,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    """OUTDATED

     This endpoint only exists so that some old clients do not throw an error

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[InternalServerErrorError500, InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401, None, YouMustBelongToAnOrganizationToUploadAFileError403]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        None,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    """OUTDATED

     This endpoint only exists so that some old clients do not throw an error

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[InternalServerErrorError500, InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401, None, YouMustBelongToAnOrganizationToUploadAFileError403]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        None,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    """OUTDATED

     This endpoint only exists so that some old clients do not throw an error

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[InternalServerErrorError500, InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401, None, YouMustBelongToAnOrganizationToUploadAFileError403]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
