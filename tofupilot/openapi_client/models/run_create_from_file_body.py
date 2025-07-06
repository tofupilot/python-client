from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.run_create_from_file_body_importer import RunCreateFromFileBodyImporter

T = TypeVar("T", bound="RunCreateFromFileBody")


@_attrs_define
class RunCreateFromFileBody:
    upload_id: UUID
    importer: RunCreateFromFileBodyImporter
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        upload_id = str(self.upload_id)

        importer = self.importer.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "upload_id": upload_id,
                "importer": importer,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        upload_id = UUID(d.pop("upload_id"))

        importer = RunCreateFromFileBodyImporter(d.pop("importer"))

        run_create_from_file_body = cls(
            upload_id=upload_id,
            importer=importer,
        )

        run_create_from_file_body.additional_properties = d
        return run_create_from_file_body

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
