from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.run_get_response_200_data_item_outcome import RunGetResponse200DataItemOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_get_response_200_data_item_attachments_item import RunGetResponse200DataItemAttachmentsItem
    from ..models.run_get_response_200_data_item_created_by_station_type_0 import (
        RunGetResponse200DataItemCreatedByStationType0,
    )
    from ..models.run_get_response_200_data_item_created_by_user_type_0 import (
        RunGetResponse200DataItemCreatedByUserType0,
    )
    from ..models.run_get_response_200_data_item_phases_item import RunGetResponse200DataItemPhasesItem
    from ..models.run_get_response_200_data_item_procedure_type_0 import RunGetResponse200DataItemProcedureType0
    from ..models.run_get_response_200_data_item_procedure_version_type_0 import (
        RunGetResponse200DataItemProcedureVersionType0,
    )
    from ..models.run_get_response_200_data_item_unit_type_0 import RunGetResponse200DataItemUnitType0


T = TypeVar("T", bound="RunGetResponse200DataItem")


@_attrs_define
class RunGetResponse200DataItem:
    id: str
    outcome: RunGetResponse200DataItemOutcome
    started_at: str
    created_at: str
    duration: Union[Unset, Any] = UNSET
    created_by_user: Union["RunGetResponse200DataItemCreatedByUserType0", None, Unset] = UNSET
    created_by_station: Union["RunGetResponse200DataItemCreatedByStationType0", None, Unset] = UNSET
    procedure: Union["RunGetResponse200DataItemProcedureType0", None, Unset] = UNSET
    unit: Union["RunGetResponse200DataItemUnitType0", None, Unset] = UNSET
    phases: Union[Unset, list["RunGetResponse200DataItemPhasesItem"]] = UNSET
    procedure_version: Union["RunGetResponse200DataItemProcedureVersionType0", None, Unset] = UNSET
    attachments: Union[Unset, list["RunGetResponse200DataItemAttachmentsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.run_get_response_200_data_item_created_by_station_type_0 import (
            RunGetResponse200DataItemCreatedByStationType0,
        )
        from ..models.run_get_response_200_data_item_created_by_user_type_0 import (
            RunGetResponse200DataItemCreatedByUserType0,
        )
        from ..models.run_get_response_200_data_item_procedure_type_0 import RunGetResponse200DataItemProcedureType0
        from ..models.run_get_response_200_data_item_procedure_version_type_0 import (
            RunGetResponse200DataItemProcedureVersionType0,
        )
        from ..models.run_get_response_200_data_item_unit_type_0 import RunGetResponse200DataItemUnitType0

        id = self.id

        outcome = self.outcome.value

        started_at = self.started_at

        created_at = self.created_at

        duration = self.duration

        created_by_user: Union[None, Unset, dict[str, Any]]
        if isinstance(self.created_by_user, Unset):
            created_by_user = UNSET
        elif isinstance(self.created_by_user, RunGetResponse200DataItemCreatedByUserType0):
            created_by_user = self.created_by_user.to_dict()
        else:
            created_by_user = self.created_by_user

        created_by_station: Union[None, Unset, dict[str, Any]]
        if isinstance(self.created_by_station, Unset):
            created_by_station = UNSET
        elif isinstance(self.created_by_station, RunGetResponse200DataItemCreatedByStationType0):
            created_by_station = self.created_by_station.to_dict()
        else:
            created_by_station = self.created_by_station

        procedure: Union[None, Unset, dict[str, Any]]
        if isinstance(self.procedure, Unset):
            procedure = UNSET
        elif isinstance(self.procedure, RunGetResponse200DataItemProcedureType0):
            procedure = self.procedure.to_dict()
        else:
            procedure = self.procedure

        unit: Union[None, Unset, dict[str, Any]]
        if isinstance(self.unit, Unset):
            unit = UNSET
        elif isinstance(self.unit, RunGetResponse200DataItemUnitType0):
            unit = self.unit.to_dict()
        else:
            unit = self.unit

        phases: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.phases, Unset):
            phases = []
            for phases_item_data in self.phases:
                phases_item = phases_item_data.to_dict()
                phases.append(phases_item)

        procedure_version: Union[None, Unset, dict[str, Any]]
        if isinstance(self.procedure_version, Unset):
            procedure_version = UNSET
        elif isinstance(self.procedure_version, RunGetResponse200DataItemProcedureVersionType0):
            procedure_version = self.procedure_version.to_dict()
        else:
            procedure_version = self.procedure_version

        attachments: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "outcome": outcome,
                "startedAt": started_at,
                "createdAt": created_at,
            }
        )
        if duration is not UNSET:
            field_dict["duration"] = duration
        if created_by_user is not UNSET:
            field_dict["createdByUser"] = created_by_user
        if created_by_station is not UNSET:
            field_dict["createdByStation"] = created_by_station
        if procedure is not UNSET:
            field_dict["procedure"] = procedure
        if unit is not UNSET:
            field_dict["unit"] = unit
        if phases is not UNSET:
            field_dict["phases"] = phases
        if procedure_version is not UNSET:
            field_dict["procedureVersion"] = procedure_version
        if attachments is not UNSET:
            field_dict["attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_get_response_200_data_item_attachments_item import RunGetResponse200DataItemAttachmentsItem
        from ..models.run_get_response_200_data_item_created_by_station_type_0 import (
            RunGetResponse200DataItemCreatedByStationType0,
        )
        from ..models.run_get_response_200_data_item_created_by_user_type_0 import (
            RunGetResponse200DataItemCreatedByUserType0,
        )
        from ..models.run_get_response_200_data_item_phases_item import RunGetResponse200DataItemPhasesItem
        from ..models.run_get_response_200_data_item_procedure_type_0 import RunGetResponse200DataItemProcedureType0
        from ..models.run_get_response_200_data_item_procedure_version_type_0 import (
            RunGetResponse200DataItemProcedureVersionType0,
        )
        from ..models.run_get_response_200_data_item_unit_type_0 import RunGetResponse200DataItemUnitType0

        d = dict(src_dict)
        id = d.pop("id")

        outcome = RunGetResponse200DataItemOutcome(d.pop("outcome"))

        started_at = d.pop("startedAt")

        created_at = d.pop("createdAt")

        duration = d.pop("duration", UNSET)

        def _parse_created_by_user(data: object) -> Union["RunGetResponse200DataItemCreatedByUserType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                created_by_user_type_0 = RunGetResponse200DataItemCreatedByUserType0.from_dict(data)

                return created_by_user_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunGetResponse200DataItemCreatedByUserType0", None, Unset], data)

        created_by_user = _parse_created_by_user(d.pop("createdByUser", UNSET))

        def _parse_created_by_station(
            data: object,
        ) -> Union["RunGetResponse200DataItemCreatedByStationType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                created_by_station_type_0 = RunGetResponse200DataItemCreatedByStationType0.from_dict(data)

                return created_by_station_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunGetResponse200DataItemCreatedByStationType0", None, Unset], data)

        created_by_station = _parse_created_by_station(d.pop("createdByStation", UNSET))

        def _parse_procedure(data: object) -> Union["RunGetResponse200DataItemProcedureType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                procedure_type_0 = RunGetResponse200DataItemProcedureType0.from_dict(data)

                return procedure_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunGetResponse200DataItemProcedureType0", None, Unset], data)

        procedure = _parse_procedure(d.pop("procedure", UNSET))

        def _parse_unit(data: object) -> Union["RunGetResponse200DataItemUnitType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                unit_type_0 = RunGetResponse200DataItemUnitType0.from_dict(data)

                return unit_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunGetResponse200DataItemUnitType0", None, Unset], data)

        unit = _parse_unit(d.pop("unit", UNSET))

        phases = []
        _phases = d.pop("phases", UNSET)
        for phases_item_data in _phases or []:
            phases_item = RunGetResponse200DataItemPhasesItem.from_dict(phases_item_data)

            phases.append(phases_item)

        def _parse_procedure_version(
            data: object,
        ) -> Union["RunGetResponse200DataItemProcedureVersionType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                procedure_version_type_0 = RunGetResponse200DataItemProcedureVersionType0.from_dict(data)

                return procedure_version_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunGetResponse200DataItemProcedureVersionType0", None, Unset], data)

        procedure_version = _parse_procedure_version(d.pop("procedureVersion", UNSET))

        attachments = []
        _attachments = d.pop("attachments", UNSET)
        for attachments_item_data in _attachments or []:
            attachments_item = RunGetResponse200DataItemAttachmentsItem.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        run_get_response_200_data_item = cls(
            id=id,
            outcome=outcome,
            started_at=started_at,
            created_at=created_at,
            duration=duration,
            created_by_user=created_by_user,
            created_by_station=created_by_station,
            procedure=procedure,
            unit=unit,
            phases=phases,
            procedure_version=procedure_version,
            attachments=attachments,
        )

        run_get_response_200_data_item.additional_properties = d
        return run_get_response_200_data_item

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
