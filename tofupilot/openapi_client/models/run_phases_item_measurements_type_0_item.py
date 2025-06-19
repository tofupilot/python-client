from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.run_phases_item_measurements_type_0_item_outcome import RunPhasesItemMeasurementsType0ItemOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_phases_item_measurements_type_0_item_measured_value_type_4_type_0 import (
        RunPhasesItemMeasurementsType0ItemMeasuredValueType4Type0,
    )


T = TypeVar("T", bound="RunPhasesItemMeasurementsType0Item")


@_attrs_define
class RunPhasesItemMeasurementsType0Item:
    name: str
    outcome: RunPhasesItemMeasurementsType0ItemOutcome
    measured_value: Union[
        "RunPhasesItemMeasurementsType0ItemMeasuredValueType4Type0",
        None,
        Unset,
        bool,
        float,
        list[Any],
        list[list[float]],
        str,
    ] = UNSET
    units: Union[None, Unset, list[str], str] = UNSET
    lower_limit: Union[Unset, float] = UNSET
    upper_limit: Union[Unset, float] = UNSET
    validators: Union[None, Unset, list[str]] = UNSET
    docstring: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.run_phases_item_measurements_type_0_item_measured_value_type_4_type_0 import (
            RunPhasesItemMeasurementsType0ItemMeasuredValueType4Type0,
        )

        name = self.name

        outcome = self.outcome.value

        measured_value: Union[None, Unset, bool, dict[str, Any], float, list[Any], list[list[float]], str]
        if isinstance(self.measured_value, Unset):
            measured_value = UNSET
        elif isinstance(self.measured_value, list):
            measured_value = []
            for measured_value_type_3_item_data in self.measured_value:
                measured_value_type_3_item = measured_value_type_3_item_data

                measured_value.append(measured_value_type_3_item)

        elif isinstance(self.measured_value, RunPhasesItemMeasurementsType0ItemMeasuredValueType4Type0):
            measured_value = self.measured_value.to_dict()
        elif isinstance(self.measured_value, list):
            measured_value = self.measured_value

        else:
            measured_value = self.measured_value

        units: Union[None, Unset, list[str], str]
        if isinstance(self.units, Unset):
            units = UNSET
        elif isinstance(self.units, list):
            units = self.units

        else:
            units = self.units

        lower_limit = self.lower_limit

        upper_limit = self.upper_limit

        validators: Union[None, Unset, list[str]]
        if isinstance(self.validators, Unset):
            validators = UNSET
        elif isinstance(self.validators, list):
            validators = self.validators

        else:
            validators = self.validators

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
            }
        )
        if measured_value is not UNSET:
            field_dict["measured_value"] = measured_value
        if units is not UNSET:
            field_dict["units"] = units
        if lower_limit is not UNSET:
            field_dict["lower_limit"] = lower_limit
        if upper_limit is not UNSET:
            field_dict["upper_limit"] = upper_limit
        if validators is not UNSET:
            field_dict["validators"] = validators
        if docstring is not UNSET:
            field_dict["docstring"] = docstring

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_phases_item_measurements_type_0_item_measured_value_type_4_type_0 import (
            RunPhasesItemMeasurementsType0ItemMeasuredValueType4Type0,
        )

        d = dict(src_dict)
        name = d.pop("name")

        outcome = RunPhasesItemMeasurementsType0ItemOutcome(d.pop("outcome"))

        def _parse_measured_value(
            data: object,
        ) -> Union[
            "RunPhasesItemMeasurementsType0ItemMeasuredValueType4Type0",
            None,
            Unset,
            bool,
            float,
            list[Any],
            list[list[float]],
            str,
        ]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                measured_value_type_3 = []
                _measured_value_type_3 = data
                for measured_value_type_3_item_data in _measured_value_type_3:
                    measured_value_type_3_item = cast(list[float], measured_value_type_3_item_data)

                    measured_value_type_3.append(measured_value_type_3_item)

                return measured_value_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                measured_value_type_4_type_0 = RunPhasesItemMeasurementsType0ItemMeasuredValueType4Type0.from_dict(data)

                return measured_value_type_4_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, list):
                    raise TypeError()
                measured_value_type_4_type_1 = cast(list[Any], data)

                return measured_value_type_4_type_1
            except:  # noqa: E722
                pass
            return cast(
                Union[
                    "RunPhasesItemMeasurementsType0ItemMeasuredValueType4Type0",
                    None,
                    Unset,
                    bool,
                    float,
                    list[Any],
                    list[list[float]],
                    str,
                ],
                data,
            )

        measured_value = _parse_measured_value(d.pop("measured_value", UNSET))

        def _parse_units(data: object) -> Union[None, Unset, list[str], str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                units_type_1 = cast(list[str], data)

                return units_type_1
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str], str], data)

        units = _parse_units(d.pop("units", UNSET))

        lower_limit = d.pop("lower_limit", UNSET)

        upper_limit = d.pop("upper_limit", UNSET)

        def _parse_validators(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                validators_type_0 = cast(list[str], data)

                return validators_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        validators = _parse_validators(d.pop("validators", UNSET))

        def _parse_docstring(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        docstring = _parse_docstring(d.pop("docstring", UNSET))

        run_phases_item_measurements_type_0_item = cls(
            name=name,
            outcome=outcome,
            measured_value=measured_value,
            units=units,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            validators=validators,
            docstring=docstring,
        )

        run_phases_item_measurements_type_0_item.additional_properties = d
        return run_phases_item_measurements_type_0_item

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
