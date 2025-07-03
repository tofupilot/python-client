import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RunStepsItem")


@_attrs_define
class RunStepsItem:
    name: str
    step_passed: bool
    duration: str
    started_at: datetime.datetime
    measurement_unit: Union[None, Unset, str] = UNSET
    measurement_value: Union[None, Unset, float, str] = UNSET
    str_value: Union[None, Unset, str] = UNSET
    limit_low: Union[Unset, float] = UNSET
    limit_high: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        step_passed = self.step_passed

        duration = self.duration

        started_at = self.started_at.isoformat()

        measurement_unit: Union[None, Unset, str]
        if isinstance(self.measurement_unit, Unset):
            measurement_unit = UNSET
        else:
            measurement_unit = self.measurement_unit

        measurement_value: Union[None, Unset, float, str]
        if isinstance(self.measurement_value, Unset):
            measurement_value = UNSET
        else:
            measurement_value = self.measurement_value

        str_value: Union[None, Unset, str]
        if isinstance(self.str_value, Unset):
            str_value = UNSET
        else:
            str_value = self.str_value

        limit_low = self.limit_low

        limit_high = self.limit_high

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "step_passed": step_passed,
                "duration": duration,
                "started_at": started_at,
            }
        )
        if measurement_unit is not UNSET:
            field_dict["measurement_unit"] = measurement_unit
        if measurement_value is not UNSET:
            field_dict["measurement_value"] = measurement_value
        if str_value is not UNSET:
            field_dict["str_value"] = str_value
        if limit_low is not UNSET:
            field_dict["limit_low"] = limit_low
        if limit_high is not UNSET:
            field_dict["limit_high"] = limit_high

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        step_passed = d.pop("step_passed")

        duration = d.pop("duration")

        started_at = isoparse(d.pop("started_at"))

        def _parse_measurement_unit(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        measurement_unit = _parse_measurement_unit(d.pop("measurement_unit", UNSET))

        def _parse_measurement_value(data: object) -> Union[None, Unset, float, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float, str], data)

        measurement_value = _parse_measurement_value(d.pop("measurement_value", UNSET))

        def _parse_str_value(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        str_value = _parse_str_value(d.pop("str_value", UNSET))

        limit_low = d.pop("limit_low", UNSET)

        limit_high = d.pop("limit_high", UNSET)

        run_steps_item = cls(
            name=name,
            step_passed=step_passed,
            duration=duration,
            started_at=started_at,
            measurement_unit=measurement_unit,
            measurement_value=measurement_value,
            str_value=str_value,
            limit_low=limit_low,
            limit_high=limit_high,
        )

        run_steps_item.additional_properties = d
        return run_steps_item

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
