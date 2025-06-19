from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RunUnitUnderTest")


@_attrs_define
class RunUnitUnderTest:
    serial_number: str
    part_name: Union[None, Unset, str] = UNSET
    """ The `part_name` field is now ignored by `create_run`. You can safely remove it from your scripts. """
    part_number: Union[Unset, str] = UNSET
    batch_number: Union[Unset, str] = UNSET
    revision: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        serial_number = self.serial_number

        part_name: Union[None, Unset, str]
        if isinstance(self.part_name, Unset):
            part_name = UNSET
        else:
            part_name = self.part_name

        part_number = self.part_number

        batch_number = self.batch_number

        revision = self.revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "serial_number": serial_number,
            }
        )
        if part_name is not UNSET:
            field_dict["part_name"] = part_name
        if part_number is not UNSET:
            field_dict["part_number"] = part_number
        if batch_number is not UNSET:
            field_dict["batch_number"] = batch_number
        if revision is not UNSET:
            field_dict["revision"] = revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        serial_number = d.pop("serial_number")

        def _parse_part_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        part_name = _parse_part_name(d.pop("part_name", UNSET))

        part_number = d.pop("part_number", UNSET)

        batch_number = d.pop("batch_number", UNSET)

        revision = d.pop("revision", UNSET)

        run_unit_under_test = cls(
            serial_number=serial_number,
            part_name=part_name,
            part_number=part_number,
            batch_number=batch_number,
            revision=revision,
        )

        run_unit_under_test.additional_properties = d
        return run_unit_under_test

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
