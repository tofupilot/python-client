from typing import Literal, cast

StreamingGetStreamingTokenResponse200PublishOptionsQosType2 = Literal[2]

STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_PUBLISH_OPTIONS_QOS_TYPE_2_VALUES: set[
    StreamingGetStreamingTokenResponse200PublishOptionsQosType2
] = {
    2,
}


def check_streaming_get_streaming_token_response_200_publish_options_qos_type_2(
    value: int,
) -> StreamingGetStreamingTokenResponse200PublishOptionsQosType2:
    if value in STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_PUBLISH_OPTIONS_QOS_TYPE_2_VALUES:
        return cast(StreamingGetStreamingTokenResponse200PublishOptionsQosType2, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_PUBLISH_OPTIONS_QOS_TYPE_2_VALUES!r}"
    )
