# Parts
(*parts*)

## Overview

### Available Operations

* [list](#list) - List and filter parts
* [create](#create) - Create part
* [get](#get) - Get part
* [delete](#delete) - Delete part
* [update](#update) - Update part

## list

Retrieve a paginated list of parts and components in your organization. Filter and search by part name, number, or revision number for inventory management.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.parts.list(limit=50, cursor=50, search_query="PCB", sort_by="created_at", sort_order="desc")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                               | Type                                                                    | Required                                                                | Description                                                             | Example                                                                 |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `limit`                                                                 | *Optional[int]*                                                         | :heavy_minus_sign:                                                      | Maximum number of parts to return in a single page.                     | 50                                                                      |
| `cursor`                                                                | *Optional[int]*                                                         | :heavy_minus_sign:                                                      | N/A                                                                     | 50                                                                      |
| `search_query`                                                          | *Optional[str]*                                                         | :heavy_minus_sign:                                                      | N/A                                                                     | PCB                                                                     |
| `procedure_ids`                                                         | List[*str*]                                                             | :heavy_minus_sign:                                                      | N/A                                                                     |                                                                         |
| `sort_by`                                                               | [Optional[models.PartListSortBy]](../../models/partlistsortby.md)       | :heavy_minus_sign:                                                      | Field to sort results by.                                               | created_at                                                              |
| `sort_order`                                                            | [Optional[models.PartListSortOrder]](../../models/partlistsortorder.md) | :heavy_minus_sign:                                                      | Sort order direction.                                                   | desc                                                                    |
| `retries`                                                               | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)        | :heavy_minus_sign:                                                      | Configuration to override the default retry behavior of the client.     |                                                                         |

### Response

**[models.PartListResponse](../../models/partlistresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## create

Create a new part. Optionally create with a revision. Part numbers are matched case-insensitively (e.g., "PART-001" and "part-001" are considered the same).

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.parts.create(number="PCB-V2.0", name="Main PCB Board", revision_number="REV-A")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                            | Type                                                                                                 | Required                                                                                             | Description                                                                                          | Example                                                                                              |
| ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `number`                                                                                             | *str*                                                                                                | :heavy_check_mark:                                                                                   | Unique identifier number for the part.                                                               | PCB-V2.0                                                                                             |
| `name`                                                                                               | *Optional[str]*                                                                                      | :heavy_minus_sign:                                                                                   | Human-readable name for the part. If not provided, a default name will be used.                      | Main PCB Board                                                                                       |
| `revision_number`                                                                                    | *Optional[str]*                                                                                      | :heavy_minus_sign:                                                                                   | Revision identifier for the part version. If not provided, default revision identifier will be used. | REV-A                                                                                                |
| `retries`                                                                                            | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                     | :heavy_minus_sign:                                                                                   | Configuration to override the default retry behavior of the client.                                  |                                                                                                      |

### Response

**[models.PartCreateResponse](../../models/partcreateresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## get

Retrieve a single part by its number, including all revisions, metadata, and linked units. Part numbers are matched case-insensitively.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.parts.get(number="PCB-MAIN-001")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `number`                                                            | *str*                                                               | :heavy_check_mark:                                                  | Part number of the part to retrieve.                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.PartGetResponse](../../models/partgetresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## delete

Permanently delete a part and all its revisions. This removes all associated data and cannot be undone.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.parts.delete(number="<value>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `number`                                                            | *str*                                                               | :heavy_check_mark:                                                  | Part number to delete.                                              |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.PartDeleteResponse](../../models/partdeleteresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## update

Update a part's number or name. Identifies the part by its current number in the URL with case-insensitive matching.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.parts.update(number="PCB-V2.0", new_number="PCB-V3.0", name="Updated PCB Board")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `number`                                                            | *str*                                                               | :heavy_check_mark:                                                  | Part number of the part to update.                                  |                                                                     |
| `new_number`                                                        | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | New unique identifier number for the part.                          | PCB-V3.0                                                            |
| `name`                                                              | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | New human-readable name for the part.                               | Updated PCB Board                                                   |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.PartUpdateResponse](../../models/partupdateresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |