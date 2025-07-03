from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.circular_parent_relationship_not_allowed_sub_units_not_found_error_400 import (
    CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
)
from ...models.failed_to_generate_upload_url_error_502 import FailedToGenerateUploadURLError502
from ...models.internal_server_error_error_500 import InternalServerErrorError500
from ...models.unit_not_found_serial_number_error_404 import UnitNotFoundSerialNumberError404
from ...models.upload_initialize_body import UploadInitializeBody
from ...models.upload_initialize_response_200 import UploadInitializeResponse200
from ...models.you_must_belong_to_an_organization_to_upload_a_file_error_403 import (
    YouMustBelongToAnOrganizationToUploadAFileError403,
)
from ...types import Response


def _get_kwargs(
    *,
    body: UploadInitializeBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/uploads/initialize",
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
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadInitializeResponse200,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    if response.status_code == 200:
        response_200 = UploadInitializeResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = CircularParentRelationshipNotAllowedSubUnitsNotFoundError400.from_dict(response.json())

        return response_400
    if response.status_code == 403:
        response_403 = YouMustBelongToAnOrganizationToUploadAFileError403.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = UnitNotFoundSerialNumberError404.from_dict(response.json())

        return response_404
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
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadInitializeResponse200,
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
    body: UploadInitializeBody,
) -> Response[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadInitializeResponse200,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    """Initialize file upload

     Creates a temporary upload URL for a file and returns it along with the upload ID

    Args:
        body (UploadInitializeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, FailedToGenerateUploadURLError502, InternalServerErrorError500, UnitNotFoundSerialNumberError404, UploadInitializeResponse200, YouMustBelongToAnOrganizationToUploadAFileError403]]
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
    body: UploadInitializeBody,
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadInitializeResponse200,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    """Initialize file upload

     Creates a temporary upload URL for a file and returns it along with the upload ID

    Args:
        body (UploadInitializeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, FailedToGenerateUploadURLError502, InternalServerErrorError500, UnitNotFoundSerialNumberError404, UploadInitializeResponse200, YouMustBelongToAnOrganizationToUploadAFileError403]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: UploadInitializeBody,
) -> Response[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadInitializeResponse200,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    """Initialize file upload

     Creates a temporary upload URL for a file and returns it along with the upload ID

    Args:
        body (UploadInitializeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, FailedToGenerateUploadURLError502, InternalServerErrorError500, UnitNotFoundSerialNumberError404, UploadInitializeResponse200, YouMustBelongToAnOrganizationToUploadAFileError403]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: UploadInitializeBody,
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        FailedToGenerateUploadURLError502,
        InternalServerErrorError500,
        UnitNotFoundSerialNumberError404,
        UploadInitializeResponse200,
        YouMustBelongToAnOrganizationToUploadAFileError403,
    ]
]:
    """Initialize file upload

     Creates a temporary upload URL for a file and returns it along with the upload ID

    Args:
        body (UploadInitializeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, FailedToGenerateUploadURLError502, InternalServerErrorError500, UnitNotFoundSerialNumberError404, UploadInitializeResponse200, YouMustBelongToAnOrganizationToUploadAFileError403]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
