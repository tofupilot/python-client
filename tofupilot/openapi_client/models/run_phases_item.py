from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.run_phases_item_outcome import RunPhasesItemOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_phases_item_measurements_type_0_item import RunPhasesItemMeasurementsType0Item


T = TypeVar("T", bound="RunPhasesItem")


@_attrs_define
class RunPhasesItem:
    name: str
    outcome: RunPhasesItemOutcome
    start_time_millis: float
    end_time_millis: float
    measurements: Union[None, Unset, list["RunPhasesItemMeasurementsType0Item"]] = UNSET
    docstring: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        outcome = self.outcome.value

        start_time_millis = self.start_time_millis

        end_time_millis = self.end_time_millis

        measurements: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.measurements, Unset):
            measurements = UNSET
        elif isinstance(self.measurements, list):
            measurements = []
            for measurements_type_0_item_data in self.measurements:
                measurements_type_0_item = measurements_type_0_item_data.to_dict()
                measurements.append(measurements_type_0_item)

        else:
            measurements = self.measurements

        docstring: Union[None, Unset, str]
        if isinstance(self.docstring, Unset):
            docstring = UNSET
        else:
            docstring = self.docstring

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "outcome": outcome,
                "start_time_millis": start_time_millis,
                "end_time_millis": end_time_millis,
            }
        )
        if measurements is not UNSET:
            field_dict["measurements"] = measurements
        if docstring is not UNSET:
            field_dict["docstring"] = docstring

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_phases_item_measurements_type_0_item import RunPhasesItemMeasurementsType0Item

        d = dict(src_dict)
        name = d.pop("name")

        outcome = RunPhasesItemOutcome(d.pop("outcome"))

        start_time_millis = d.pop("start_time_millis")

        end_time_millis = d.pop("end_time_millis")

        def _parse_measurements(data: object) -> Union[None, Unset, list["RunPhasesItemMeasurementsType0Item"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                measurements_type_0 = []
                _measurements_type_0 = data
                for measurements_type_0_item_data in _measurements_type_0:
                    measurements_type_0_item = RunPhasesItemMeasurementsType0Item.from_dict(
                        measurements_type_0_item_data
                    )

                    measurements_type_0.append(measurements_type_0_item)

                return measurements_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["RunPhasesItemMeasurementsType0Item"]], data)

        measurements = _parse_measurements(d.pop("measurements", UNSET))

        def _parse_docstring(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        docstring = _parse_docstring(d.pop("docstring", UNSET))

        run_phases_item = cls(
            name=name,
            outcome=outcome,
            start_time_millis=start_time_millis,
            end_time_millis=end_time_millis,
            measurements=measurements,
            docstring=docstring,
        )

        run_phases_item.additional_properties = d
        return run_phases_item

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
