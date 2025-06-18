from typing import Literal, cast

StreamingGetStreamingTokenResponse200SubscribeOptionsQosType0 = Literal[0]

STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_SUBSCRIBE_OPTIONS_QOS_TYPE_0_VALUES: set[
    StreamingGetStreamingTokenResponse200SubscribeOptionsQosType0
] = {
    0,
}


def check_streaming_get_streaming_token_response_200_subscribe_options_qos_type_0(
    value: int,
) -> StreamingGetStreamingTokenResponse200SubscribeOptionsQosType0:
    if value in STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_SUBSCRIBE_OPTIONS_QOS_TYPE_0_VALUES:
        return cast(StreamingGetStreamingTokenResponse200SubscribeOptionsQosType0, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_SUBSCRIBE_OPTIONS_QOS_TYPE_0_VALUES!r}"
    )
