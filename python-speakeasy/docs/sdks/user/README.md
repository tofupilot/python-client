# User
(*user*)

## Overview

### Available Operations

* [list](#list) - List users

## list

Retrieve a list of users in your organization. Use the current parameter to get only the authenticated user profile and permissions.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.user.list(current=True)

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `current`                                                           | *Optional[bool]*                                                    | :heavy_minus_sign:                                                  | If true, returns only the current authenticated user                | true                                                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[List[models.UserListResponse]](../../models/.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |