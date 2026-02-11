"""TofuPilot SDK with enhanced error tracking and logging capabilities."""

import json
import os
from typing import Optional, Union

import httpx
from pydantic_core import ValidationError

from .sdk import TofuPilot
from .errors.tofupiloterror import TofuPilotError
from ._hooks.types import AfterSuccessContext, AfterSuccessHook
from ..banner import print_banner_and_check_version


def _enhance_error_message(e: TofuPilotError) -> None:
    """Enhance a TofuPilotError with validation issue details before re-raising."""
    if hasattr(e, "data") and hasattr(e.data, "issues") and e.data.issues:
        details = "; ".join(issue.message for issue in e.data.issues)
        object.__setattr__(e, "message", f"{e.message}: {details}")


class _WarningHook(AfterSuccessHook):
    """Surface server-side warnings from X-Warnings response header."""

    def after_success(
        self, hook_ctx: AfterSuccessContext, response: httpx.Response
    ) -> Union[httpx.Response, Exception]:
        raw = response.headers.get("x-warnings")
        if not raw:
            return response
        try:
            server_warnings = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            return response
        for w in server_warnings:
            print(f"\033[33m[TofuPilot] Warning: {w}\033[0m")
        return response


class TofuPilotValidationError(Exception):
    """Clear validation error for TofuPilot SDK."""
    pass


def _format_validation_error(e: ValidationError) -> str:
    """Format all pydantic validation errors into a clear message."""
    lines = []
    for error in e.errors():
        loc = " → ".join(str(segment) for segment in error.get('loc', ()))
        msg = error.get('msg', '')
        input_value = error.get('input')
        line = f"  {loc}: {msg}"
        if input_value is not None:
            line += f" (got {input_value!r})"
        lines.append(line)
    return "Invalid input:\n" + "\n".join(lines)


class _ResourceWithBetterErrors:
    """Wraps any SDK resource to enhance TofuPilotError messages with validation details."""

    def __init__(self, resource):
        self._resource = resource

    def __getattr__(self, name):
        attr = getattr(self._resource, name)
        if not callable(attr):
            return attr

        def wrapper(*args, **kwargs):
            try:
                return attr(*args, **kwargs)
            except TofuPilotError as e:
                _enhance_error_message(e)
                raise

        return wrapper


class _RunsWithBetterErrors(_ResourceWithBetterErrors):
    """Extends resource wrapper with ValidationError handling for runs.create."""

    def create(self, **kwargs):
        try:
            return self._resource.create(**kwargs)
        except TofuPilotError as e:
            _enhance_error_message(e)
            raise
        except ValidationError as e:
            raise TofuPilotValidationError(_format_validation_error(e)) from None


class TofuPilotWithErrorTracking(TofuPilot):
    """
    Enhanced TofuPilot client with automatic error tracking and improved logging.

    This wrapper extends the base TofuPilot SDK with:
    - Automatic error tracking and categorization
    - Enhanced logging for debugging
    - Better error context and suggestions
    - Transparent API - all original methods work exactly the same
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        retry_config=None,
        debug: bool = False,
        **kwargs
    ):
        """
        Initialize TofuPilot client with error tracking.

        Args:
            api_key: API key for authentication
            server_url: Override default server URL
            timeout_ms: Request timeout in milliseconds
            retry_config: Retry configuration
            debug: Enable debug logging
            **kwargs: Additional arguments passed to base SDK
        """

        if api_key is None:
            api_key = os.environ.get("TOFUPILOT_API_KEY", None)

        # Initialize base SDK
        super().__init__(
            api_key=api_key,
            server_url=server_url,
            timeout_ms=timeout_ms,
            retry_config=retry_config,
            **kwargs
        )

        print_banner_and_check_version()

        # Register warning hook to surface server-side warnings
        hooks = self.sdk_configuration.__dict__["_hooks"]
        hooks.register_after_success_hook(_WarningHook())

    def __getattr__(self, name: str):
        attr = super().__getattr__(name)
        if name == 'runs':
            attr = _RunsWithBetterErrors(attr)
        else:
            attr = _ResourceWithBetterErrors(attr)
        setattr(self, name, attr)
        return attr
