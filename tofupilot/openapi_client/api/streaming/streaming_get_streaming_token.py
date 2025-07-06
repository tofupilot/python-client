from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.failed_to_generate_upload_url_error_502 import FailedToGenerateUploadURLError502
from ...models.internal_server_error_error_500 import InternalServerErrorError500
from ...models.invalid_api_key_please_verify_your_key_and_try_again_error_401 import (
    InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
)
from ...models.streaming_get_streaming_token_response_200 import StreamingGetStreamingTokenResponse200
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/streaming",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        StreamingGetStreamingTokenResponse200,
    ]
]:
    if response.status_code == 200:
        response_200 = StreamingGetStreamingTokenResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401.from_dict(response.json())

        return response_401
    if response.status_code == 500:
        response_500 = InternalServerErrorError500.from_dict(response.json())

        return response_500
    if response.status_code == 502:
        response_502 = FailedToGenerateUploadURLError502.from_dict(response.json())

        return response_502
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        StreamingGetStreamingTokenResponse200,
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
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        StreamingGetStreamingTokenResponse200,
    ]
]:
    """Get a streaming token

     Returns a token and URL for connecting to an EMQX server, as well as the publish and subscribe
    options, notably the topic

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FailedToGenerateUploadURLError502, InternalServerErrorError500, InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401, StreamingGetStreamingTokenResponse200]]
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
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        StreamingGetStreamingTokenResponse200,
    ]
]:
    """Get a streaming token

     Returns a token and URL for connecting to an EMQX server, as well as the publish and subscribe
    options, notably the topic

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FailedToGenerateUploadURLError502, InternalServerErrorError500, InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401, StreamingGetStreamingTokenResponse200]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        StreamingGetStreamingTokenResponse200,
    ]
]:
    """Get a streaming token

     Returns a token and URL for connecting to an EMQX server, as well as the publish and subscribe
    options, notably the topic

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FailedToGenerateUploadURLError502, InternalServerErrorError500, InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401, StreamingGetStreamingTokenResponse200]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401,
        StreamingGetStreamingTokenResponse200,
    ]
]:
    """Get a streaming token

     Returns a token and URL for connecting to an EMQX server, as well as the publish and subscribe
    options, notably the topic

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FailedToGenerateUploadURLError502, InternalServerErrorError500, InvalidAPIKeyPleaseVerifyYourKeyAndTryAgainError401, StreamingGetStreamingTokenResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
