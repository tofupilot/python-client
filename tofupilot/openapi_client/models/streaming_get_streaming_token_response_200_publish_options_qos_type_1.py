from typing import Literal, cast

StreamingGetStreamingTokenResponse200PublishOptionsQosType1 = Literal[1]

STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_PUBLISH_OPTIONS_QOS_TYPE_1_VALUES: set[
    StreamingGetStreamingTokenResponse200PublishOptionsQosType1
] = {
    1,
}


def check_streaming_get_streaming_token_response_200_publish_options_qos_type_1(
    value: int,
) -> StreamingGetStreamingTokenResponse200PublishOptionsQosType1:
    if value in STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_PUBLISH_OPTIONS_QOS_TYPE_1_VALUES:
        return cast(StreamingGetStreamingTokenResponse200PublishOptionsQosType1, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {STREAMING_GET_STREAMING_TOKEN_RESPONSE_200_PUBLISH_OPTIONS_QOS_TYPE_1_VALUES!r}"
    )
