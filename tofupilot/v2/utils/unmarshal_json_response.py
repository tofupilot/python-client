"""TofuPilot SDK Runtime. DO NOT EDIT — maintained in clients/generator/runtime/."""

from typing import Any, Optional

import httpx

from .serializers import unmarshal_json
from tofupilot.v2 import errors


def unmarshal_json_response(
    typ: Any, http_res: httpx.Response, body: Optional[str] = None
) -> Any:
    if body is None:
        body = http_res.text
    try:
        return unmarshal_json(body, typ)
    except Exception as e:
        raise errors.ResponseValidationError(
            "Response validation failed",
            http_res,
            e,
            body,
        ) from e
