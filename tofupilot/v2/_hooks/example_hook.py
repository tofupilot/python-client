from typing import Optional, Tuple, Union

import httpx

from .types import (
    AfterErrorContext,
    AfterErrorHook,
    AfterSuccessContext,
    AfterSuccessHook,
    BeforeRequestContext,
    BeforeRequestHook,
    SDKConfiguration,
    SDKInitHook,
)

class ExampleHook(SDKInitHook, BeforeRequestHook, AfterSuccessHook, AfterErrorHook):

    def sdk_init(self, config: SDKConfiguration) -> SDKConfiguration:
        # modify the SDK configuration, base_url, or wrap the client used by the SDK here and return the
        # updated configuration
        # Access config.base_url, config.client, and other configuration options

        return config

    def before_request(
        self, hook_ctx: BeforeRequestContext, request: httpx.Request
    ) -> Union[httpx.Request, Exception]:
        # Access SDK configuration: hook_ctx.config
        # Access operation details: hook_ctx.operation_id, hook_ctx.base_url
        # modify the request object before it is sent, such as adding headers or query
        # parameters, or raise an exception to stop the request

        print("before_request")

        return request

    def after_success(
        self, hook_ctx: AfterSuccessContext, response: httpx.Response
    ) -> Union[httpx.Response, Exception]:
        # Access SDK configuration: hook_ctx.config
        # Access operation details: hook_ctx.operation_id, hook_ctx.base_url
        # modify the response object before deserialization or raise an exception to stop
        # the response from being returned

        print("after_success")

        return response

    def after_error(
        self,
        hook_ctx: AfterErrorContext,
        response: Optional[httpx.Response],
        error: Optional[Exception],
    ) -> Union[Tuple[Optional[httpx.Response], Optional[Exception]], Exception]:
        # Access SDK configuration: hook_ctx.config
        # Access operation details: hook_ctx.operation_id, hook_ctx.base_url
        # modify the response before it is deserialized as a custom error or the error
        # object before it is returned or raise an exception to stop processing of other
        # error hooks and return early

        return response, error