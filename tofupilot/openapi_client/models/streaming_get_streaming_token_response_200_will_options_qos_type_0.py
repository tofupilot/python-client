from typing import Literal, cast

StreamingGetStreamingTokenResponse200WillOptionsQosType0 = Literal[0]

STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_WILL_OPTIONS_QOS_TYPE_0_VALUES: set[
    StreamingGetStreamingTokenResponse200WillOptionsQosType0
] = {
    0,
}


def check_streaming_get_streaming_token_response_200_will_options_qos_type_0(
    value: int,
) -> StreamingGetStreamingTokenResponse200WillOptionsQosType0:
    if value in STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_WILL_OPTIONS_QOS_TYPE_0_VALUES:
        return cast(StreamingGetStreamingTokenResponse200WillOptionsQosType0, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_WILL_OPTIONS_QOS_TYPE_0_VALUES!r}"
    )
