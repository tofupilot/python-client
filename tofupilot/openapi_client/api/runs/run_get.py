import datetime
from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.circular_parent_relationship_not_allowed_sub_units_not_found_error_400 import (
    CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
)
from ...models.internal_server_error_error_500 import InternalServerErrorError500
from ...models.run_get_exclude_item import RunGetExcludeItem
from ...models.run_get_outcome import RunGetOutcome
from ...models.run_get_response_200 import RunGetResponse200
from ...models.run_get_sort import RunGetSort
from ...models.unit_not_found_serial_number_error_404 import UnitNotFoundSerialNumberError404
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    ids: Union[Unset, list[UUID]] = UNSET,
    unit_serial_numbers: Union[Unset, list[str]] = UNSET,
    procedure_ids: Union[Unset, list[UUID]] = UNSET,
    created_by_user_id: Union[Unset, UUID] = UNSET,
    created_by_station_id: Union[Unset, UUID] = UNSET,
    outcome: Union[Unset, RunGetOutcome] = UNSET,
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort: Union[Unset, RunGetSort] = RunGetSort.VALUE_0,
    exclude: Union[Unset, list[RunGetExcludeItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(ids, Unset):
        json_ids = []
        for ids_item_data in ids:
            ids_item = str(ids_item_data)
            json_ids.append(ids_item)

    params["ids"] = json_ids

    json_unit_serial_numbers: Union[Unset, list[str]] = UNSET
    if not isinstance(unit_serial_numbers, Unset):
        json_unit_serial_numbers = unit_serial_numbers

    params["unitSerialNumbers"] = json_unit_serial_numbers

    json_procedure_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(procedure_ids, Unset):
        json_procedure_ids = []
        for procedure_ids_item_data in procedure_ids:
            procedure_ids_item = str(procedure_ids_item_data)
            json_procedure_ids.append(procedure_ids_item)

    params["procedureIds"] = json_procedure_ids

    json_created_by_user_id: Union[Unset, str] = UNSET
    if not isinstance(created_by_user_id, Unset):
        json_created_by_user_id = str(created_by_user_id)
    params["createdByUserId"] = json_created_by_user_id

    json_created_by_station_id: Union[Unset, str] = UNSET
    if not isinstance(created_by_station_id, Unset):
        json_created_by_station_id = str(created_by_station_id)
    params["createdByStationId"] = json_created_by_station_id

    json_outcome: Union[Unset, str] = UNSET
    if not isinstance(outcome, Unset):
        json_outcome = outcome.value

    params["outcome"] = json_outcome

    json_start_date: Union[Unset, str] = UNSET
    if not isinstance(start_date, Unset):
        json_start_date = start_date.isoformat()
    params["startDate"] = json_start_date

    json_end_date: Union[Unset, str] = UNSET
    if not isinstance(end_date, Unset):
        json_end_date = end_date.isoformat()
    params["endDate"] = json_end_date

    params["limit"] = limit

    params["offset"] = offset

    json_sort: Union[Unset, str] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    json_exclude: Union[Unset, list[str]] = UNSET
    if not isinstance(exclude, Unset):
        json_exclude = []
        for exclude_item_data in exclude:
            exclude_item = exclude_item_data.value
            json_exclude.append(exclude_item)

    params["exclude"] = json_exclude

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/runs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunGetResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    if response.status_code == 200:
        response_200 = RunGetResponse200.from_dict(response.json())

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
        RunGetResponse200,
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
    ids: Union[Unset, list[UUID]] = UNSET,
    unit_serial_numbers: Union[Unset, list[str]] = UNSET,
    procedure_ids: Union[Unset, list[UUID]] = UNSET,
    created_by_user_id: Union[Unset, UUID] = UNSET,
    created_by_station_id: Union[Unset, UUID] = UNSET,
    outcome: Union[Unset, RunGetOutcome] = UNSET,
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort: Union[Unset, RunGetSort] = RunGetSort.VALUE_0,
    exclude: Union[Unset, list[RunGetExcludeItem]] = UNSET,
) -> Response[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunGetResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Get runs along various filters.

    Args:
        ids (Union[Unset, list[UUID]]):
        unit_serial_numbers (Union[Unset, list[str]]):
        procedure_ids (Union[Unset, list[UUID]]):
        created_by_user_id (Union[Unset, UUID]):
        created_by_station_id (Union[Unset, UUID]):
        outcome (Union[Unset, RunGetOutcome]):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
        limit (Union[Unset, int]): Maximum number of runs to return (default 50, min 1, max 100)
            Default: 50.
        offset (Union[Unset, int]): Number of runs to skip for pagination (default 0) Default: 0.
        sort (Union[Unset, RunGetSort]):  Default: RunGetSort.VALUE_0.
        exclude (Union[Unset, list[RunGetExcludeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, RunGetResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        ids=ids,
        unit_serial_numbers=unit_serial_numbers,
        procedure_ids=procedure_ids,
        created_by_user_id=created_by_user_id,
        created_by_station_id=created_by_station_id,
        outcome=outcome,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        sort=sort,
        exclude=exclude,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    ids: Union[Unset, list[UUID]] = UNSET,
    unit_serial_numbers: Union[Unset, list[str]] = UNSET,
    procedure_ids: Union[Unset, list[UUID]] = UNSET,
    created_by_user_id: Union[Unset, UUID] = UNSET,
    created_by_station_id: Union[Unset, UUID] = UNSET,
    outcome: Union[Unset, RunGetOutcome] = UNSET,
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort: Union[Unset, RunGetSort] = RunGetSort.VALUE_0,
    exclude: Union[Unset, list[RunGetExcludeItem]] = UNSET,
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunGetResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Get runs along various filters.

    Args:
        ids (Union[Unset, list[UUID]]):
        unit_serial_numbers (Union[Unset, list[str]]):
        procedure_ids (Union[Unset, list[UUID]]):
        created_by_user_id (Union[Unset, UUID]):
        created_by_station_id (Union[Unset, UUID]):
        outcome (Union[Unset, RunGetOutcome]):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
        limit (Union[Unset, int]): Maximum number of runs to return (default 50, min 1, max 100)
            Default: 50.
        offset (Union[Unset, int]): Number of runs to skip for pagination (default 0) Default: 0.
        sort (Union[Unset, RunGetSort]):  Default: RunGetSort.VALUE_0.
        exclude (Union[Unset, list[RunGetExcludeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, RunGetResponse200, UnitNotFoundSerialNumberError404]
    """

    return sync_detailed(
        client=client,
        ids=ids,
        unit_serial_numbers=unit_serial_numbers,
        procedure_ids=procedure_ids,
        created_by_user_id=created_by_user_id,
        created_by_station_id=created_by_station_id,
        outcome=outcome,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        sort=sort,
        exclude=exclude,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    ids: Union[Unset, list[UUID]] = UNSET,
    unit_serial_numbers: Union[Unset, list[str]] = UNSET,
    procedure_ids: Union[Unset, list[UUID]] = UNSET,
    created_by_user_id: Union[Unset, UUID] = UNSET,
    created_by_station_id: Union[Unset, UUID] = UNSET,
    outcome: Union[Unset, RunGetOutcome] = UNSET,
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort: Union[Unset, RunGetSort] = RunGetSort.VALUE_0,
    exclude: Union[Unset, list[RunGetExcludeItem]] = UNSET,
) -> Response[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunGetResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Get runs along various filters.

    Args:
        ids (Union[Unset, list[UUID]]):
        unit_serial_numbers (Union[Unset, list[str]]):
        procedure_ids (Union[Unset, list[UUID]]):
        created_by_user_id (Union[Unset, UUID]):
        created_by_station_id (Union[Unset, UUID]):
        outcome (Union[Unset, RunGetOutcome]):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
        limit (Union[Unset, int]): Maximum number of runs to return (default 50, min 1, max 100)
            Default: 50.
        offset (Union[Unset, int]): Number of runs to skip for pagination (default 0) Default: 0.
        sort (Union[Unset, RunGetSort]):  Default: RunGetSort.VALUE_0.
        exclude (Union[Unset, list[RunGetExcludeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, RunGetResponse200, UnitNotFoundSerialNumberError404]]
    """

    kwargs = _get_kwargs(
        ids=ids,
        unit_serial_numbers=unit_serial_numbers,
        procedure_ids=procedure_ids,
        created_by_user_id=created_by_user_id,
        created_by_station_id=created_by_station_id,
        outcome=outcome,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        sort=sort,
        exclude=exclude,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    ids: Union[Unset, list[UUID]] = UNSET,
    unit_serial_numbers: Union[Unset, list[str]] = UNSET,
    procedure_ids: Union[Unset, list[UUID]] = UNSET,
    created_by_user_id: Union[Unset, UUID] = UNSET,
    created_by_station_id: Union[Unset, UUID] = UNSET,
    outcome: Union[Unset, RunGetOutcome] = UNSET,
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort: Union[Unset, RunGetSort] = RunGetSort.VALUE_0,
    exclude: Union[Unset, list[RunGetExcludeItem]] = UNSET,
) -> Optional[
    Union[
        CircularParentRelationshipNotAllowedSubUnitsNotFoundError400,
        InternalServerErrorError500,
        RunGetResponse200,
        UnitNotFoundSerialNumberError404,
    ]
]:
    """Get runs along various filters.

    Args:
        ids (Union[Unset, list[UUID]]):
        unit_serial_numbers (Union[Unset, list[str]]):
        procedure_ids (Union[Unset, list[UUID]]):
        created_by_user_id (Union[Unset, UUID]):
        created_by_station_id (Union[Unset, UUID]):
        outcome (Union[Unset, RunGetOutcome]):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
        limit (Union[Unset, int]): Maximum number of runs to return (default 50, min 1, max 100)
            Default: 50.
        offset (Union[Unset, int]): Number of runs to skip for pagination (default 0) Default: 0.
        sort (Union[Unset, RunGetSort]):  Default: RunGetSort.VALUE_0.
        exclude (Union[Unset, list[RunGetExcludeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CircularParentRelationshipNotAllowedSubUnitsNotFoundError400, InternalServerErrorError500, RunGetResponse200, UnitNotFoundSerialNumberError404]
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
            unit_serial_numbers=unit_serial_numbers,
            procedure_ids=procedure_ids,
            created_by_user_id=created_by_user_id,
            created_by_station_id=created_by_station_id,
            outcome=outcome,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            sort=sort,
            exclude=exclude,
        )
    ).parsed
