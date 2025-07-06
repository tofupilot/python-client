from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.streaming_get_streaming_token_response_200_subscribe_options_qos_type_0 import (
    StreamingGetStreamingTokenResponse200SubscribeOptionsQosType0,
)
from ..models.streaming_get_streaming_token_response_200_subscribe_options_qos_type_1 import (
    StreamingGetStreamingTokenResponse200SubscribeOptionsQosType1,
)
from ..models.streaming_get_streaming_token_response_200_subscribe_options_qos_type_2 import (
    StreamingGetStreamingTokenResponse200SubscribeOptionsQosType2,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="StreamingGetStreamingTokenResponse200SubscribeOptions")


@_attrs_define
class StreamingGetStreamingTokenResponse200SubscribeOptions:
    """options which will be passed to paho.mqtt.Client.subscribe"""

    topic: str
    """ topic to subscribe to """
    qos: Union[
        StreamingGetStreamingTokenResponse200SubscribeOptionsQosType0,
        StreamingGetStreamingTokenResponse200SubscribeOptionsQosType1,
        StreamingGetStreamingTokenResponse200SubscribeOptionsQosType2,
        Unset,
    ] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        topic = self.topic

        qos: Union[Unset, int]
        if isinstance(self.qos, Unset):
            qos = UNSET
        elif isinstance(self.qos, StreamingGetStreamingTokenResponse200SubscribeOptionsQosType0):
            qos = self.qos.value
        elif isinstance(self.qos, StreamingGetStreamingTokenResponse200SubscribeOptionsQosType1):
            qos = self.qos.value
        else:
            qos = self.qos.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "topic": topic,
            }
        )
        if qos is not UNSET:
            field_dict["qos"] = qos

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        topic = d.pop("topic")

        def _parse_qos(
            data: object,
        ) -> Union[
            StreamingGetStreamingTokenResponse200SubscribeOptionsQosType0,
            StreamingGetStreamingTokenResponse200SubscribeOptionsQosType1,
            StreamingGetStreamingTokenResponse200SubscribeOptionsQosType2,
            Unset,
        ]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, int):
                    raise TypeError()
                qos_type_0 = StreamingGetStreamingTokenResponse200SubscribeOptionsQosType0(data)

                return qos_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, int):
                    raise TypeError()
                qos_type_1 = StreamingGetStreamingTokenResponse200SubscribeOptionsQosType1(data)

                return qos_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, int):
                raise TypeError()
            qos_type_2 = StreamingGetStreamingTokenResponse200SubscribeOptionsQosType2(data)

            return qos_type_2

        qos = _parse_qos(d.pop("qos", UNSET))

        streaming_get_streaming_token_response_200_subscribe_options = cls(
            topic=topic,
            qos=qos,
        )

        streaming_get_streaming_token_response_200_subscribe_options.additional_properties = d
        return streaming_get_streaming_token_response_200_subscribe_options

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
