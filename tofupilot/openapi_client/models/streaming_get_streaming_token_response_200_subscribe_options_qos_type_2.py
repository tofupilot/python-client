from typing import Literal, cast

StreamingGetStreamingTokenResponse200SubscribeOptionsQosType2 = Literal[2]

STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_SUBSCRIBE_OPTIONS_QOS_TYPE_2_VALUES: set[
    StreamingGetStreamingTokenResponse200SubscribeOptionsQosType2
] = {
    2,
}


def check_streaming_get_streaming_token_response_200_subscribe_options_qos_type_2(
    value: int,
) -> StreamingGetStreamingTokenResponse200SubscribeOptionsQosType2:
    if value in STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_SUBSCRIBE_OPTIONS_QOS_TYPE_2_VALUES:
        return cast(StreamingGetStreamingTokenResponse200SubscribeOptionsQosType2, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_SUBSCRIBE_OPTIONS_QOS_TYPE_2_VALUES!r}"
    )
