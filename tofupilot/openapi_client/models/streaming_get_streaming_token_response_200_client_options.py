from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="StreamingGetStreamingTokenResponse200ClientOptions")


@_attrs_define
class StreamingGetStreamingTokenResponse200ClientOptions:
    """options which will be passed to paho.mqtt.Client"""

    transport: str
    protocol: int
    reconnect_on_failure: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        transport = self.transport

        protocol = self.protocol

        reconnect_on_failure = self.reconnect_on_failure

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "transport": transport,
                "protocol": protocol,
                "reconnect_on_failure": reconnect_on_failure,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        transport = d.pop("transport")

        protocol = d.pop("protocol")

        reconnect_on_failure = d.pop("reconnect_on_failure")

        streaming_get_streaming_token_response_200_client_options = cls(
            transport=transport,
            protocol=protocol,
            reconnect_on_failure=reconnect_on_failure,
        )

        streaming_get_streaming_token_response_200_client_options.additional_properties = d
        return streaming_get_streaming_token_response_200_client_options

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
