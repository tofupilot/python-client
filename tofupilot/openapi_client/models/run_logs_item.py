import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.run_logs_item_level import RunLogsItemLevel

T = TypeVar("T", bound="RunLogsItem")


@_attrs_define
class RunLogsItem:
    level: RunLogsItemLevel
    timestamp: datetime.datetime
    message: str
    source_file: str
    line_number: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        level = self.level.value

        timestamp = self.timestamp.isoformat()

        message = self.message

        source_file = self.source_file

        line_number = self.line_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "level": level,
                "timestamp": timestamp,
                "message": message,
                "source_file": source_file,
                "line_number": line_number,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        level = RunLogsItemLevel(d.pop("level"))

        timestamp = isoparse(d.pop("timestamp"))

        message = d.pop("message")

        source_file = d.pop("source_file")

        line_number = d.pop("line_number")

        run_logs_item = cls(
            level=level,
            timestamp=timestamp,
            message=message,
            source_file=source_file,
            line_number=line_number,
        )

        run_logs_item.additional_properties = d
        return run_logs_item

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
