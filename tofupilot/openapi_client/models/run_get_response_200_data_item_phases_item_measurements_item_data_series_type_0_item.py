from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RunGetResponse200DataItemPhasesItemMeasurementsItemDataSeriesType0Item")


@_attrs_define
class RunGetResponse200DataItemPhasesItemMeasurementsItemDataSeriesType0Item:
    data: list[float]
    units: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data

        units: Union[None, Unset, str]
        if isinstance(self.units, Unset):
            units = UNSET
        else:
            units = self.units

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )
        if units is not UNSET:
            field_dict["units"] = units

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        data = cast(list[float], d.pop("data"))

        def _parse_units(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        units = _parse_units(d.pop("units", UNSET))

        run_get_response_200_data_item_phases_item_measurements_item_data_series_type_0_item = cls(
            data=data,
            units=units,
        )

        run_get_response_200_data_item_phases_item_measurements_item_data_series_type_0_item.additional_properties = d
        return run_get_response_200_data_item_phases_item_measurements_item_data_series_type_0_item

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
