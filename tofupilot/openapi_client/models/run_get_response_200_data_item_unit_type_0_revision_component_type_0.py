from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RunGetResponse200DataItemUnitType0RevisionComponentType0")


@_attrs_define
class RunGetResponse200DataItemUnitType0RevisionComponentType0:
    part_number: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        part_number = self.part_number

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "partNumber": part_number,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        part_number = d.pop("partNumber")

        name = d.pop("name")

        run_get_response_200_data_item_unit_type_0_revision_component_type_0 = cls(
            part_number=part_number,
            name=name,
        )

        run_get_response_200_data_item_unit_type_0_revision_component_type_0.additional_properties = d
        return run_get_response_200_data_item_unit_type_0_revision_component_type_0

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
