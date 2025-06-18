from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.streaming_get_streaming_token_response_200_client_options import (
        StreamingGetStreamingTokenResponse200ClientOptions,
    )
    from ..models.streaming_get_streaming_token_response_200_connect_options import (
        StreamingGetStreamingTokenResponse200ConnectOptions,
    )
    from ..models.streaming_get_streaming_token_response_200_publish_options import (
        StreamingGetStreamingTokenResponse200PublishOptions,
    )
    from ..models.streaming_get_streaming_token_response_200_subscribe_options import (
        StreamingGetStreamingTokenResponse200SubscribeOptions,
    )
    from ..models.streaming_get_streaming_token_response_200_will_options import (
        StreamingGetStreamingTokenResponse200WillOptions,
    )


T = TypeVar("T", bound="StreamingGetStreamingTokenResponse200")


@_attrs_define
class StreamingGetStreamingTokenResponse200:
    token: str
    """ JWT used for authentication """
    operator_page: str
    client_options: "StreamingGetStreamingTokenResponse200ClientOptions"
    """ options which will be passed to paho.mqtt.Client """
    will_options: "StreamingGetStreamingTokenResponse200WillOptions"
    """ options which will be passed to paho.mqtt.Client.will_set """
    connect_options: "StreamingGetStreamingTokenResponse200ConnectOptions"
    """ options which will be passed to paho.mqtt.Client.connect """
    publish_options: "StreamingGetStreamingTokenResponse200PublishOptions"
    """ options which will be passed to paho.mqtt.Client.publish """
    subscribe_options: "StreamingGetStreamingTokenResponse200SubscribeOptions"
    """ options which will be passed to paho.mqtt.Client.subscribe """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        token = self.token

        operator_page = self.operator_page

        client_options = self.client_options.to_dict()

        will_options = self.will_options.to_dict()

        connect_options = self.connect_options.to_dict()

        publish_options = self.publish_options.to_dict()

        subscribe_options = self.subscribe_options.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "token": token,
                "operatorPage": operator_page,
                "clientOptions": client_options,
                "willOptions": will_options,
                "connectOptions": connect_options,
                "publishOptions": publish_options,
                "subscribeOptions": subscribe_options,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.streaming_get_streaming_token_response_200_client_options import (
            StreamingGetStreamingTokenResponse200ClientOptions,
        )
        from ..models.streaming_get_streaming_token_response_200_connect_options import (
            StreamingGetStreamingTokenResponse200ConnectOptions,
        )
        from ..models.streaming_get_streaming_token_response_200_publish_options import (
            StreamingGetStreamingTokenResponse200PublishOptions,
        )
        from ..models.streaming_get_streaming_token_response_200_subscribe_options import (
            StreamingGetStreamingTokenResponse200SubscribeOptions,
        )
        from ..models.streaming_get_streaming_token_response_200_will_options import (
            StreamingGetStreamingTokenResponse200WillOptions,
        )

        d = dict(src_dict)
        token = d.pop("token")

        operator_page = d.pop("operatorPage")

        client_options = StreamingGetStreamingTokenResponse200ClientOptions.from_dict(d.pop("clientOptions"))

        will_options = StreamingGetStreamingTokenResponse200WillOptions.from_dict(d.pop("willOptions"))

        connect_options = StreamingGetStreamingTokenResponse200ConnectOptions.from_dict(d.pop("connectOptions"))

        publish_options = StreamingGetStreamingTokenResponse200PublishOptions.from_dict(d.pop("publishOptions"))

        subscribe_options = StreamingGetStreamingTokenResponse200SubscribeOptions.from_dict(d.pop("subscribeOptions"))

        streaming_get_streaming_token_response_200 = cls(
            token=token,
            operator_page=operator_page,
            client_options=client_options,
            will_options=will_options,
            connect_options=connect_options,
            publish_options=publish_options,
            subscribe_options=subscribe_options,
        )

        streaming_get_streaming_token_response_200.additional_properties = d
        return streaming_get_streaming_token_response_200

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
