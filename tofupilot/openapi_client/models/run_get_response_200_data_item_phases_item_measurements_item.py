from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.run_get_response_200_data_item_phases_item_measurements_item_outcome import (
    RunGetResponse200DataItemPhasesItemMeasurementsItemOutcome,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_get_response_200_data_item_phases_item_measurements_item_data_series_type_0_item import (
        RunGetResponse200DataItemPhasesItemMeasurementsItemDataSeriesType0Item,
    )


T = TypeVar("T", bound="RunGetResponse200DataItemPhasesItemMeasurementsItem")


@_attrs_define
class RunGetResponse200DataItemPhasesItemMeasurementsItem:
    id: str
    name: str
    outcome: RunGetResponse200DataItemPhasesItemMeasurementsItemOutcome
    value: Union[None, float]
    string_value: Union[None, str]
    bool_value: Union[None, bool]
    data_series: Union[None, list["RunGetResponse200DataItemPhasesItemMeasurementsItemDataSeriesType0Item"]]
    units: Union[None, Unset, str] = UNSET
    validators: Union[None, Unset, list[str]] = UNSET
    lower_limit: Union[None, Unset, float] = UNSET
    upper_limit: Union[None, Unset, float] = UNSET
    json_value: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        outcome = self.outcome.value

        value: Union[None, float]
        value = self.value

        string_value: Union[None, str]
        string_value = self.string_value

        bool_value: Union[None, bool]
        bool_value = self.bool_value

        data_series: Union[None, list[dict[str, Any]]]
        if isinstance(self.data_series, list):
            data_series = []
            for data_series_type_0_item_data in self.data_series:
                data_series_type_0_item = data_series_type_0_item_data.to_dict()
                data_series.append(data_series_type_0_item)

        else:
            data_series = self.data_series

        units: Union[None, Unset, str]
        if isinstance(self.units, Unset):
            units = UNSET
        else:
            units = self.units

        validators: Union[None, Unset, list[str]]
        if isinstance(self.validators, Unset):
            validators = UNSET
        elif isinstance(self.validators, list):
            validators = self.validators

        else:
            validators = self.validators

        lower_limit: Union[None, Unset, float]
        if isinstance(self.lower_limit, Unset):
            lower_limit = UNSET
        else:
            lower_limit = self.lower_limit

        upper_limit: Union[None, Unset, float]
        if isinstance(self.upper_limit, Unset):
            upper_limit = UNSET
        else:
            upper_limit = self.upper_limit

        json_value = self.json_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "outcome": outcome,
                "value": value,
                "stringValue": string_value,
                "boolValue": bool_value,
                "dataSeries": data_series,
            }
        )
        if units is not UNSET:
            field_dict["units"] = units
        if validators is not UNSET:
            field_dict["validators"] = validators
        if lower_limit is not UNSET:
            field_dict["lowerLimit"] = lower_limit
        if upper_limit is not UNSET:
            field_dict["upperLimit"] = upper_limit
        if json_value is not UNSET:
            field_dict["jsonValue"] = json_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_get_response_200_data_item_phases_item_measurements_item_data_series_type_0_item import (
            RunGetResponse200DataItemPhasesItemMeasurementsItemDataSeriesType0Item,
        )

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        outcome = RunGetResponse200DataItemPhasesItemMeasurementsItemOutcome(d.pop("outcome"))

        def _parse_value(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        value = _parse_value(d.pop("value"))

        def _parse_string_value(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        string_value = _parse_string_value(d.pop("stringValue"))

        def _parse_bool_value(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        bool_value = _parse_bool_value(d.pop("boolValue"))

        def _parse_data_series(
            data: object,
        ) -> Union[None, list["RunGetResponse200DataItemPhasesItemMeasurementsItemDataSeriesType0Item"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                data_series_type_0 = []
                _data_series_type_0 = data
                for data_series_type_0_item_data in _data_series_type_0:
                    data_series_type_0_item = (
                        RunGetResponse200DataItemPhasesItemMeasurementsItemDataSeriesType0Item.from_dict(
                            data_series_type_0_item_data
                        )
                    )

                    data_series_type_0.append(data_series_type_0_item)

                return data_series_type_0
            except:  # noqa: E722
                pass
            return cast(
                Union[None, list["RunGetResponse200DataItemPhasesItemMeasurementsItemDataSeriesType0Item"]], data
            )

        data_series = _parse_data_series(d.pop("dataSeries"))

        def _parse_units(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        units = _parse_units(d.pop("units", UNSET))

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

        def _parse_lower_limit(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        lower_limit = _parse_lower_limit(d.pop("lowerLimit", UNSET))

        def _parse_upper_limit(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        upper_limit = _parse_upper_limit(d.pop("upperLimit", UNSET))

        json_value = d.pop("jsonValue", UNSET)

        run_get_response_200_data_item_phases_item_measurements_item = cls(
            id=id,
            name=name,
            outcome=outcome,
            value=value,
            string_value=string_value,
            bool_value=bool_value,
            data_series=data_series,
            units=units,
            validators=validators,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            json_value=json_value,
        )

        run_get_response_200_data_item_phases_item_measurements_item.additional_properties = d
        return run_get_response_200_data_item_phases_item_measurements_item

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
