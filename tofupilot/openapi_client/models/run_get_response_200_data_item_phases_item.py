from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.run_get_response_200_data_item_phases_item_outcome import RunGetResponse200DataItemPhasesItemOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_get_response_200_data_item_phases_item_measurements_item import (
        RunGetResponse200DataItemPhasesItemMeasurementsItem,
    )


T = TypeVar("T", bound="RunGetResponse200DataItemPhasesItem")


@_attrs_define
class RunGetResponse200DataItemPhasesItem:
    id: str
    name: str
    outcome: RunGetResponse200DataItemPhasesItemOutcome
    started_at: str
    duration: Union[Unset, Any] = UNSET
    docstring: Union[None, Unset, str] = UNSET
    measurements: Union[Unset, list["RunGetResponse200DataItemPhasesItemMeasurementsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        outcome = self.outcome.value

        started_at = self.started_at

        duration = self.duration

        docstring: Union[None, Unset, str]
        if isinstance(self.docstring, Unset):
            docstring = UNSET
        else:
            docstring = self.docstring

        measurements: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.measurements, Unset):
            measurements = []
            for measurements_item_data in self.measurements:
                measurements_item = measurements_item_data.to_dict()
                measurements.append(measurements_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "outcome": outcome,
                "startedAt": started_at,
            }
        )
        if duration is not UNSET:
            field_dict["duration"] = duration
        if docstring is not UNSET:
            field_dict["docstring"] = docstring
        if measurements is not UNSET:
            field_dict["measurements"] = measurements

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_get_response_200_data_item_phases_item_measurements_item import (
            RunGetResponse200DataItemPhasesItemMeasurementsItem,
        )

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        outcome = RunGetResponse200DataItemPhasesItemOutcome(d.pop("outcome"))

        started_at = d.pop("startedAt")

        duration = d.pop("duration", UNSET)

        def _parse_docstring(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        docstring = _parse_docstring(d.pop("docstring", UNSET))

        measurements = []
        _measurements = d.pop("measurements", UNSET)
        for measurements_item_data in _measurements or []:
            measurements_item = RunGetResponse200DataItemPhasesItemMeasurementsItem.from_dict(measurements_item_data)

            measurements.append(measurements_item)

        run_get_response_200_data_item_phases_item = cls(
            id=id,
            name=name,
            outcome=outcome,
            started_at=started_at,
            duration=duration,
            docstring=docstring,
            measurements=measurements,
        )

        run_get_response_200_data_item_phases_item.additional_properties = d
        return run_get_response_200_data_item_phases_item

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
