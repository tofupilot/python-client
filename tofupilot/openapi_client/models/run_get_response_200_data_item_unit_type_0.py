from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_get_response_200_data_item_unit_type_0_batch_type_0 import (
        RunGetResponse200DataItemUnitType0BatchType0,
    )
    from ..models.run_get_response_200_data_item_unit_type_0_revision import RunGetResponse200DataItemUnitType0Revision


T = TypeVar("T", bound="RunGetResponse200DataItemUnitType0")


@_attrs_define
class RunGetResponse200DataItemUnitType0:
    id: str
    serial_number: str
    revision: "RunGetResponse200DataItemUnitType0Revision"
    batch: Union["RunGetResponse200DataItemUnitType0BatchType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.run_get_response_200_data_item_unit_type_0_batch_type_0 import (
            RunGetResponse200DataItemUnitType0BatchType0,
        )

        id = self.id

        serial_number = self.serial_number

        revision = self.revision.to_dict()

        batch: Union[None, Unset, dict[str, Any]]
        if isinstance(self.batch, Unset):
            batch = UNSET
        elif isinstance(self.batch, RunGetResponse200DataItemUnitType0BatchType0):
            batch = self.batch.to_dict()
        else:
            batch = self.batch

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "serialNumber": serial_number,
                "revision": revision,
            }
        )
        if batch is not UNSET:
            field_dict["batch"] = batch

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_get_response_200_data_item_unit_type_0_batch_type_0 import (
            RunGetResponse200DataItemUnitType0BatchType0,
        )
        from ..models.run_get_response_200_data_item_unit_type_0_revision import (
            RunGetResponse200DataItemUnitType0Revision,
        )

        d = dict(src_dict)
        id = d.pop("id")

        serial_number = d.pop("serialNumber")

        revision = RunGetResponse200DataItemUnitType0Revision.from_dict(d.pop("revision"))

        def _parse_batch(data: object) -> Union["RunGetResponse200DataItemUnitType0BatchType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                batch_type_0 = RunGetResponse200DataItemUnitType0BatchType0.from_dict(data)

                return batch_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunGetResponse200DataItemUnitType0BatchType0", None, Unset], data)

        batch = _parse_batch(d.pop("batch", UNSET))

        run_get_response_200_data_item_unit_type_0 = cls(
            id=id,
            serial_number=serial_number,
            revision=revision,
            batch=batch,
        )

        run_get_response_200_data_item_unit_type_0.additional_properties = d
        return run_get_response_200_data_item_unit_type_0

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
