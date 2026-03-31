# UnitsSDK
(*units*)

## Overview

### Available Operations

* [list](#list) - List and filter units
* [create](#create) - Create unit
* [delete](#delete) - Delete units
* [get](#get) - Get unit
* [update](#update) - Update unit
* [add_child](#add_child) - Add sub-unit
* [remove_child](#remove_child) - Remove sub-unit

## list

Retrieve a paginated list of units with filtering by serial number, part number, and batch. Uses cursor-based pagination for efficient large dataset traversal.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.units.list(search_query="SN-001234", ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ], serial_numbers=[
        "SN-001234",
        "SN-005678",
    ], part_numbers=[
        "PCB-V1.2",
        "PCB-V1.3",
    ], revision_numbers=[
        "1.0",
        "1.1",
    ], batch_numbers=[
        "BATCH-2024-01",
        "BATCH-2024-02",
    ], procedure_ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ], outcomes=[
        "FAIL",
        "ERROR",
    ], started_after="2024-01-15T10:30:00Z", started_before="2024-01-15T11:30:00Z", latest_only=True, run_count_min=2, run_count_max=5, created_after="2024-01-15T10:30:00Z", created_before="2024-01-15T11:30:00Z", created_by_user_ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ], created_by_station_ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ], exclude_units_with_parent=True, limit=50, cursor=50, sort_by="created_at", sort_order="desc")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                                                             | Type                                                                                                                                  | Required                                                                                                                              | Description                                                                                                                           | Example                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `search_query`                                                                                                                        | *Optional[str]*                                                                                                                       | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | SN-001234                                                                                                                             |
| `ids`                                                                                                                                 | List[*str*]                                                                                                                           | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                                                                                    |
| `serial_numbers`                                                                                                                      | List[*str*]                                                                                                                           | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | [<br/>"SN-001234",<br/>"SN-005678"<br/>]                                                                                              |
| `part_numbers`                                                                                                                        | List[*str*]                                                                                                                           | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | [<br/>"PCB-V1.2",<br/>"PCB-V1.3"<br/>]                                                                                                |
| `revision_numbers`                                                                                                                    | List[*str*]                                                                                                                           | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | [<br/>"1.0",<br/>"1.1"<br/>]                                                                                                          |
| `batch_numbers`                                                                                                                       | List[*str*]                                                                                                                           | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | [<br/>"BATCH-2024-01",<br/>"BATCH-2024-02"<br/>]                                                                                      |
| `procedure_ids`                                                                                                                       | List[*str*]                                                                                                                           | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                                                                                    |
| `outcomes`                                                                                                                            | List[[models.UnitListQueryParamOutcome](../../models/unitlistqueryparamoutcome.md)]                                                   | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | [<br/>"FAIL",<br/>"ERROR"<br/>]                                                                                                       |
| `started_after`                                                                                                                       | *Optional[str]*                                                                                                                       | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | 2024-01-15T10:30:00Z                                                                                                                  |
| `started_before`                                                                                                                      | *Optional[str]*                                                                                                                       | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | 2024-01-15T11:30:00Z                                                                                                                  |
| `latest_only`                                                                                                                         | *Optional[bool]*                                                                                                                      | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | true                                                                                                                                  |
| `run_count_min`                                                                                                                       | *Optional[int]*                                                                                                                       | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | 2                                                                                                                                     |
| `run_count_max`                                                                                                                       | *Optional[int]*                                                                                                                       | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | 5                                                                                                                                     |
| `created_after`                                                                                                                       | *Optional[str]*                                                                                                                       | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | 2024-01-15T10:30:00Z                                                                                                                  |
| `created_before`                                                                                                                      | *Optional[str]*                                                                                                                       | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | 2024-01-15T11:30:00Z                                                                                                                  |
| `created_by_user_ids`                                                                                                                 | List[*str*]                                                                                                                           | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                                                                                    |
| `created_by_station_ids`                                                                                                              | List[*str*]                                                                                                                           | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                                                                                    |
| `exclude_units_with_parent`                                                                                                           | *Optional[bool]*                                                                                                                      | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | true                                                                                                                                  |
| `limit`                                                                                                                               | *Optional[int]*                                                                                                                       | :heavy_minus_sign:                                                                                                                    | Maximum number of units to return.                                                                                                    | 50                                                                                                                                    |
| `cursor`                                                                                                                              | *Optional[int]*                                                                                                                       | :heavy_minus_sign:                                                                                                                    | N/A                                                                                                                                   | 50                                                                                                                                    |
| `sort_by`                                                                                                                             | [Optional[models.UnitListSortBy]](../../models/unitlistsortby.md)                                                                     | :heavy_minus_sign:                                                                                                                    | Field to sort results by. last_run_at sorts by most recent test run date. last_run_procedure sorts by procedure name of the last run. | created_at                                                                                                                            |
| `sort_order`                                                                                                                          | [Optional[models.UnitListSortOrder]](../../models/unitlistsortorder.md)                                                               | :heavy_minus_sign:                                                                                                                    | Sort order direction.                                                                                                                 | desc                                                                                                                                  |
| `retries`                                                                                                                             | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                                      | :heavy_minus_sign:                                                                                                                    | Configuration to override the default retry behavior of the client.                                                                   |                                                                                                                                       |

### Response

**[models.UnitListResponse](../../models/unitlistresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## create

Create a new unit with a serial number and link it to a part revision. Units represent individual hardware items tracked for manufacturing traceability.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.units.create(serial_number="SN-001234", part_number="PCB-V1.2", revision_number="REV-1.0")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                                              | Type                                                                                                                   | Required                                                                                                               | Description                                                                                                            | Example                                                                                                                |
| ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `serial_number`                                                                                                        | *str*                                                                                                                  | :heavy_check_mark:                                                                                                     | Unique serial number identifier for the unit. Must be unique within the organization.                                  | SN-001234                                                                                                              |
| `part_number`                                                                                                          | *str*                                                                                                                  | :heavy_check_mark:                                                                                                     | Component part number that defines what type of unit this is. If the part does not exist, it will be created.          | PCB-V1.2                                                                                                               |
| `revision_number`                                                                                                      | *str*                                                                                                                  | :heavy_check_mark:                                                                                                     | Hardware revision identifier for the specific version of the part. If the revision does not exist, it will be created. | REV-1.0                                                                                                                |
| `retries`                                                                                                              | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                       | :heavy_minus_sign:                                                                                                     | Configuration to override the default retry behavior of the client.                                                    |                                                                                                                        |

### Response

**[models.UnitCreateResponse](../../models/unitcreateresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## delete

Permanently delete units by serial number. This action will remove all nested elements and relationships associated with the units.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.units.delete(serial_numbers=[
        "UNIT-001",
        "UNIT-002",
    ])

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `serial_numbers`                                                    | List[*str*]                                                         | :heavy_check_mark:                                                  | Array of unit serial numbers to delete.                             | [<br/>"UNIT-001",<br/>"UNIT-002"<br/>]                              |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.UnitDeleteResponse](../../models/unitdeleteresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## get

Retrieve a single unit by its serial number. Returns comprehensive unit data including part information, parent/child relationships, and test run history.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.units.get(serial_number="SN-001234")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `serial_number`                                                     | *str*                                                               | :heavy_check_mark:                                                  | Serial number of the unit to retrieve.                              |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.UnitGetResponse](../../models/unitgetresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## update

Update unit properties including serial number, part revision, batch assignment, and file attachments with case-insensitive matching.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.units.update(serial_number="UNIT-12345", new_serial_number="UNIT-12345-NEW", part_number="PCB-V2.0", revision_number="REV-B", batch_number="BATCH-2024-02", attachments=[
        "550e8400-e29b-41d4-a716-446655440000",
    ])

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `serial_number`                                                     | *str*                                                               | :heavy_check_mark:                                                  | Serial number of the unit to update.                                |                                                                     |
| `new_serial_number`                                                 | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | New serial number for the unit.                                     | UNIT-12345-NEW                                                      |
| `part_number`                                                       | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | New part number for the unit.                                       | PCB-V2.0                                                            |
| `revision_number`                                                   | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | New revision number for the unit.                                   | REV-B                                                               |
| `batch_number`                                                      | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | New batch number for the unit. Set to null to remove batch.         | BATCH-2024-02                                                       |
| `attachments`                                                       | List[*str*]                                                         | :heavy_minus_sign:                                                  | Array of upload IDs to attach to the unit.                          | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                  |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.UnitUpdateResponse](../../models/unitupdateresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## add_child

Add a sub-unit to a parent unit to track component assemblies and multi-level hardware traceability.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.units.add_child(serial_number="UNIT-001", child_serial_number="SUB-001")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `serial_number`                                                     | *str*                                                               | :heavy_check_mark:                                                  | Serial number of the parent unit                                    |                                                                     |
| `child_serial_number`                                               | *str*                                                               | :heavy_check_mark:                                                  | Serial number of the sub-unit to add                                | SUB-001                                                             |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.UnitAddChildResponse](../../models/unitaddchildresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## remove_child

Remove a sub-unit relationship from a parent unit by serial number. Only unlinks the parent-child relationship; neither unit is deleted from the system.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.units.remove_child(serial_number="UNIT-001", child_serial_number="SUB-001")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `serial_number`                                                     | *str*                                                               | :heavy_check_mark:                                                  | Serial number of the parent unit                                    |                                                                     |
| `child_serial_number`                                               | *str*                                                               | :heavy_check_mark:                                                  | Serial number of the sub-unit to remove                             | SUB-001                                                             |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.UnitRemoveChildResponse](../../models/unitremovechildresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |