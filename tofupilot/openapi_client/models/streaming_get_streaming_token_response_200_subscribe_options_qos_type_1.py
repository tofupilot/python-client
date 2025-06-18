from typing import Literal, cast

StreamingGetStreamingTokenResponse200SubscribeOptionsQosType1 = Literal[1]

STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_SUBSCRIBE_OPTIONS_QOS_TYPE_1_VALUES: set[
    StreamingGetStreamingTokenResponse200SubscribeOptionsQosType1
] = {
    1,
}


def check_streaming_get_streaming_token_response_200_subscribe_options_qos_type_1(
    value: int,
) -> StreamingGetStreamingTokenResponse200SubscribeOptionsQosType1:
    if value in STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_SUBSCRIBE_OPTIONS_QOS_TYPE_1_VALUES:
        return cast(StreamingGetStreamingTokenResponse200SubscribeOptionsQosType1, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_SUBSCRIBE_OPTIONS_QOS_TYPE_1_VALUES!r}"
    )
