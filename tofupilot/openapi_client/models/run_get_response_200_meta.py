from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RunGetResponse200Meta")


@_attrs_define
class RunGetResponse200Meta:
    total: float
    limit: Union[None, float]
    offset: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        limit: Union[None, float]
        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total = d.pop("total")

        def _parse_limit(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        limit = _parse_limit(d.pop("limit"))

        offset = d.pop("offset")

        run_get_response_200_meta = cls(
            total=total,
            limit=limit,
            offset=offset,
        )

        run_get_response_200_meta.additional_properties = d
        return run_get_response_200_meta

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
