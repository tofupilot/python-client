from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_get_response_200_data_item_unit_type_0_revision_component_type_0 import (
        RunGetResponse200DataItemUnitType0RevisionComponentType0,
    )
    from ..models.run_get_response_200_data_item_unit_type_0_revision_image_type_0 import (
        RunGetResponse200DataItemUnitType0RevisionImageType0,
    )


T = TypeVar("T", bound="RunGetResponse200DataItemUnitType0Revision")


@_attrs_define
class RunGetResponse200DataItemUnitType0Revision:
    id: str
    identifier: str
    component: Union["RunGetResponse200DataItemUnitType0RevisionComponentType0", None]
    image: Union["RunGetResponse200DataItemUnitType0RevisionImageType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.run_get_response_200_data_item_unit_type_0_revision_component_type_0 import (
            RunGetResponse200DataItemUnitType0RevisionComponentType0,
        )
        from ..models.run_get_response_200_data_item_unit_type_0_revision_image_type_0 import (
            RunGetResponse200DataItemUnitType0RevisionImageType0,
        )

        id = self.id

        identifier = self.identifier

        component: Union[None, dict[str, Any]]
        if isinstance(self.component, RunGetResponse200DataItemUnitType0RevisionComponentType0):
            component = self.component.to_dict()
        else:
            component = self.component

        image: Union[None, Unset, dict[str, Any]]
        if isinstance(self.image, Unset):
            image = UNSET
        elif isinstance(self.image, RunGetResponse200DataItemUnitType0RevisionImageType0):
            image = self.image.to_dict()
        else:
            image = self.image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "identifier": identifier,
                "component": component,
            }
        )
        if image is not UNSET:
            field_dict["image"] = image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_get_response_200_data_item_unit_type_0_revision_component_type_0 import (
            RunGetResponse200DataItemUnitType0RevisionComponentType0,
        )
        from ..models.run_get_response_200_data_item_unit_type_0_revision_image_type_0 import (
            RunGetResponse200DataItemUnitType0RevisionImageType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        identifier = d.pop("identifier")

        def _parse_component(data: object) -> Union["RunGetResponse200DataItemUnitType0RevisionComponentType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                component_type_0 = RunGetResponse200DataItemUnitType0RevisionComponentType0.from_dict(data)

                return component_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunGetResponse200DataItemUnitType0RevisionComponentType0", None], data)

        component = _parse_component(d.pop("component"))

        def _parse_image(data: object) -> Union["RunGetResponse200DataItemUnitType0RevisionImageType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                image_type_0 = RunGetResponse200DataItemUnitType0RevisionImageType0.from_dict(data)

                return image_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunGetResponse200DataItemUnitType0RevisionImageType0", None, Unset], data)

        image = _parse_image(d.pop("image", UNSET))

        run_get_response_200_data_item_unit_type_0_revision = cls(
            id=id,
            identifier=identifier,
            component=component,
            image=image,
        )

        run_get_response_200_data_item_unit_type_0_revision.additional_properties = d
        return run_get_response_200_data_item_unit_type_0_revision

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
