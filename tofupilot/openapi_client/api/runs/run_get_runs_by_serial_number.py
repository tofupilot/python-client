from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.circular_parent_relationship_not_allowed_sub_units_not_found_error_400 import (
    CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
)
from ...models.internal_server_error_error_500 import InternalServerErrorError500
from ...models.multiple_procedures_found_with_name_procedure_name_multiple_components_found_part_number_must_be_provided_to_identify_which_component_to_use_multiple_revisions_found_for_part_number_part_number_error_409 import (
    MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409,
)
from ...models.organization_is_required_but_not_specified_in_the_request_error_403 import (
    OrganizationIsRequiredButNotSpecifiedInTheRequestError403,
)
from ...models.run_get_runs_by_serial_number_response_200 import RunGetRunsBySerialNumberResponse200
from ...models.unit_not_found_serial_number_error_404 import UnitNotFoundSerialNumberError404
from ...types import UNSET, Response


def _get_kwargs(
    *,
    serial_number: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["serial_number"] = serial_number

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/runs_serialNumber",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409,
        OrganizationIsRequiredButNotSpecifiedInTheRequestError403,
        RunGetRunsBySerialNumberResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    if response.status_code == 200:
        response_200 = RunGetRunsBySerialNumberResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = CircularParentRelationshipNotAllowedSubUnitsNotFoundError400.from_dict(response.json())

        return response_400
    if response.status_code == 403:
        response_403 = OrganizationIsRequiredButNotSpecifiedInTheRequestError403.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = UnitNotFoundSerialNumberError404.from_dict(response.json())

        return response_404
    if response.status_code == 409:
        response_409 = MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409.from_dict(
            response.json()
        )

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
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409,
        OrganizationIsRequiredButNotSpecifiedInTheRequestError403,
        RunGetRunsBySerialNumberResponse200,
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
    serial_number: str,
) -> Response[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409,
        OrganizationIsRequiredButNotSpecifiedInTheRequestError403,
        RunGetRunsBySerialNumberResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Get runs by serial number

     Retrieves all runs associated with a specific unit identified by serial number

    Args:
        serial_number (str): The serial number of the unit to get runs for

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409, OrganizationIsRequiredButNotSpecifiedInTheRequestError403, RunGetRunsBySerialNumberResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        serial_number=serial_number,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    serial_number: str,
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409,
        OrganizationIsRequiredButNotSpecifiedInTheRequestError403,
        RunGetRunsBySerialNumberResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Get runs by serial number

     Retrieves all runs associated with a specific unit identified by serial number

    Args:
        serial_number (str): The serial number of the unit to get runs for

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409, OrganizationIsRequiredButNotSpecifiedInTheRequestError403, RunGetRunsBySerialNumberResponse200, UnitNotFoundSerialNumberError404]
    """

    return sync_detailed(
        client=client,
        serial_number=serial_number,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    serial_number: str,
) -> Response[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409,
        OrganizationIsRequiredButNotSpecifiedInTheRequestError403,
        RunGetRunsBySerialNumberResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Get runs by serial number

     Retrieves all runs associated with a specific unit identified by serial number

    Args:
        serial_number (str): The serial number of the unit to get runs for

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409, OrganizationIsRequiredButNotSpecifiedInTheRequestError403, RunGetRunsBySerialNumberResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        serial_number=serial_number,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    serial_number: str,
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409,
        OrganizationIsRequiredButNotSpecifiedInTheRequestError403,
        RunGetRunsBySerialNumberResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Get runs by serial number

     Retrieves all runs associated with a specific unit identified by serial number

    Args:
        serial_number (str): The serial number of the unit to get runs for

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409, OrganizationIsRequiredButNotSpecifiedInTheRequestError403, RunGetRunsBySerialNumberResponse200, UnitNotFoundSerialNumberError404]
    """

    return (
        await asyncio_detailed(
            client=client,
            serial_number=serial_number,
        )
    ).parsed
