# Versions
(*procedures.versions*)

## Overview

### Available Operations

* [get](#get) - Get procedure version
* [delete](#delete) - Delete procedure version
* [create](#create) - Create procedure version

## get

Retrieve a single procedure version by its tag, including version metadata and configuration details.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.procedures.versions.get(procedure_id="550e8400-e29b-41d4-a716-446655440000", tag="v1.0.0")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `procedure_id`                                                      | *str*                                                               | :heavy_check_mark:                                                  | ID of the procedure that owns this version.                         |
| `tag`                                                               | *str*                                                               | :heavy_check_mark:                                                  | Version tag to retrieve.                                            |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.ProcedureGetVersionResponse](../../models/proceduregetversionresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## delete

Permanently delete a procedure version by its tag. This removes the version record and all associated configuration data and cannot be undone.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.procedures.versions.delete(procedure_id="550e8400-e29b-41d4-a716-446655440000", tag="v1.0.0")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `procedure_id`                                                      | *str*                                                               | :heavy_check_mark:                                                  | ID of the procedure that owns this version                          |
| `tag`                                                               | *str*                                                               | :heavy_check_mark:                                                  | Version tag to delete                                               |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.ProcedureDeleteVersionResponse](../../models/proceduredeleteversionresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## create

Create a new version for an existing test procedure. Versions let you track procedure changes over time and maintain a history of test configurations.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.procedures.versions.create(procedure_id="d288e698-b4c2-45d1-ad1f-f8ab3499329a", tag="v1.0.0")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `procedure_id`                                                      | *str*                                                               | :heavy_check_mark:                                                  | The ID of the procedure this version belongs to                     |                                                                     |
| `tag`                                                               | *str*                                                               | :heavy_check_mark:                                                  | The version tag                                                     | v1.0.0                                                              |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.ProcedureCreateVersionResponse](../../models/procedurecreateversionresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |