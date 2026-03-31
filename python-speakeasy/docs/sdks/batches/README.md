# Batches
(*batches*)

## Overview

### Available Operations

* [get](#get) - Get batch
* [delete](#delete) - Delete batch
* [update](#update) - Update batch
* [list](#list) - List and filter batches
* [create](#create) - Create batch

## get

Retrieve a single batch by its number, including all associated units, serial numbers, and part revisions.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.batches.get(number="BATCH-2024-001")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `number`                                                            | *str*                                                               | :heavy_check_mark:                                                  | Number of the batch to retrieve.                                    |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.BatchGetResponse](../../models/batchgetresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## delete

Permanently delete a batch by number. Units associated with the batch will be disassociated but not deleted. No nested elements are removed.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.batches.delete(number="<value>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `number`                                                            | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.BatchDeleteResponse](../../models/batchdeleteresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## update

Update a batch number. The current batch number is specified in the URL path with case-insensitive matching.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.batches.update(number="<value>", new_number="BATCH-2024-002")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `number`                                                            | *str*                                                               | :heavy_check_mark:                                                  | Current batch number to update.                                     |                                                                     |
| `new_number`                                                        | *str*                                                               | :heavy_check_mark:                                                  | New batch number.                                                   | BATCH-2024-002                                                      |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.BatchUpdateResponse](../../models/batchupdateresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## list

Retrieve batches with associated units, serial numbers, and part revisions using cursor-based pagination.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.batches.list(ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ], numbers=[
        "BATCH-2024-01",
        "BATCH-2024-02",
    ], created_after="2024-01-15T10:30:00Z", created_before="2024-01-15T11:30:00Z", limit=50, cursor=0, search_query="BATCH-2024", part_numbers=[
        "PCB-V1.2",
        "PCB-V1.3",
    ], revision_numbers=[
        "1.0",
        "1.1",
    ], sort_by="created_at", sort_order="desc")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                      | Type                                                                           | Required                                                                       | Description                                                                    | Example                                                                        |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| `ids`                                                                          | List[*str*]                                                                    | :heavy_minus_sign:                                                             | N/A                                                                            | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                             |
| `numbers`                                                                      | List[*str*]                                                                    | :heavy_minus_sign:                                                             | N/A                                                                            | [<br/>"BATCH-2024-01",<br/>"BATCH-2024-02"<br/>]                               |
| `created_after`                                                                | *Optional[str]*                                                                | :heavy_minus_sign:                                                             | N/A                                                                            | 2024-01-15T10:30:00Z                                                           |
| `created_before`                                                               | *Optional[str]*                                                                | :heavy_minus_sign:                                                             | N/A                                                                            | 2024-01-15T11:30:00Z                                                           |
| `limit`                                                                        | *Optional[int]*                                                                | :heavy_minus_sign:                                                             | Maximum number of batches to return. Use `cursor` to fetch additional results. | 50                                                                             |
| `cursor`                                                                       | *Optional[int]*                                                                | :heavy_minus_sign:                                                             | N/A                                                                            | 0                                                                              |
| `search_query`                                                                 | *Optional[str]*                                                                | :heavy_minus_sign:                                                             | N/A                                                                            | BATCH-2024                                                                     |
| `part_numbers`                                                                 | List[*str*]                                                                    | :heavy_minus_sign:                                                             | N/A                                                                            | [<br/>"PCB-V1.2",<br/>"PCB-V1.3"<br/>]                                         |
| `revision_numbers`                                                             | List[*str*]                                                                    | :heavy_minus_sign:                                                             | N/A                                                                            | [<br/>"1.0",<br/>"1.1"<br/>]                                                   |
| `sort_by`                                                                      | [Optional[models.BatchListSortBy]](../../models/batchlistsortby.md)            | :heavy_minus_sign:                                                             | Field to sort results by.                                                      | created_at                                                                     |
| `sort_order`                                                                   | [Optional[models.BatchListSortOrder]](../../models/batchlistsortorder.md)      | :heavy_minus_sign:                                                             | Sort order direction.                                                          | desc                                                                           |
| `retries`                                                                      | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)               | :heavy_minus_sign:                                                             | Configuration to override the default retry behavior of the client.            |                                                                                |

### Response

**[models.BatchListResponse](../../models/batchlistresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## create

Create a new batch without any units attached. Batch numbers are matched case-insensitively (e.g., "BATCH-001" and "batch-001" are considered the same).

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.batches.create(number="<value>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `number`                                                            | *str*                                                               | :heavy_check_mark:                                                  | The batch number identifier                                         |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.BatchCreateResponse](../../models/batchcreateresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |