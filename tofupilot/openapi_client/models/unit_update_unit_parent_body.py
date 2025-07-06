from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.unit_update_unit_parent_body_sub_units_item import UnitUpdateUnitParentBodySubUnitsItem


T = TypeVar("T", bound="UnitUpdateUnitParentBody")


@_attrs_define
class UnitUpdateUnitParentBody:
    sub_units: list["UnitUpdateUnitParentBodySubUnitsItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sub_units = []
        for sub_units_item_data in self.sub_units:
            sub_units_item = sub_units_item_data.to_dict()
            sub_units.append(sub_units_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sub_units": sub_units,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.unit_update_unit_parent_body_sub_units_item import UnitUpdateUnitParentBodySubUnitsItem

        d = dict(src_dict)
        sub_units = []
        _sub_units = d.pop("sub_units")
        for sub_units_item_data in _sub_units:
            sub_units_item = UnitUpdateUnitParentBodySubUnitsItem.from_dict(sub_units_item_data)

            sub_units.append(sub_units_item)

        unit_update_unit_parent_body = cls(
            sub_units=sub_units,
        )

        unit_update_unit_parent_body.additional_properties = d
        return unit_update_unit_parent_body

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
