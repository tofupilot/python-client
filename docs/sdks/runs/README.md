# Runs
(*runs*)

## Overview

### Available Operations

* [list](#list) - List and filter runs
* [create](#create) - Create run
* [delete](#delete) - Delete runs
* [get](#get) - Get run
* [update](#update) - Update run

## list

Retrieve a paginated list of test runs with filtering by unit, procedure, date range, outcome, and station.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot
from tofupilot.v2.utils import parse_datetime


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.runs.list(search_query="SN-001234", ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ], outcomes=[
        "PASS",
        "FAIL",
    ], procedure_ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ], procedure_versions=[
        "v1.0.0",
        "v2.0.0",
    ], serial_numbers=[
        "SN-001234",
        "SN-005678",
    ], part_numbers=[
        "PCB-V1.2",
        "PCB-V1.3",
    ], revision_numbers=[
        "REV-A",
        "REV-B",
    ], batch_numbers=[
        "BATCH-2024-Q1-001",
        "BATCH-2024-Q1-002",
    ], duration_min="PT5M", duration_max="PT30M", started_after=parse_datetime("2024-01-15T10:30:00Z"), started_before=parse_datetime("2024-01-15T11:30:00Z"), ended_after=parse_datetime("2024-01-15T10:30:00Z"), ended_before=parse_datetime("2024-01-15T11:30:00Z"), created_after=parse_datetime("2024-01-15T10:30:00Z"), created_before=parse_datetime("2024-01-15T11:30:00Z"), created_by_user_ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ], created_by_station_ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ], operated_by_ids=[
        "550e8400-e29b-41d4-a716-446655440001",
    ], limit=20, cursor=50, sort_by="started_at", sort_order="desc")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                         | Type                                                                              | Required                                                                          | Description                                                                       | Example                                                                           |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `search_query`                                                                    | *Optional[str]*                                                                   | :heavy_minus_sign:                                                                | N/A                                                                               | SN-001234                                                                         |
| `ids`                                                                             | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                                |
| `outcomes`                                                                        | List[[models.RunListQueryParamOutcome](../../models/runlistqueryparamoutcome.md)] | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"PASS",<br/>"FAIL"<br/>]                                                    |
| `procedure_ids`                                                                   | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                                |
| `procedure_versions`                                                              | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"v1.0.0",<br/>"v2.0.0"<br/>]                                                |
| `serial_numbers`                                                                  | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"SN-001234",<br/>"SN-005678"<br/>]                                          |
| `part_numbers`                                                                    | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"PCB-V1.2",<br/>"PCB-V1.3"<br/>]                                            |
| `revision_numbers`                                                                | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"REV-A",<br/>"REV-B"<br/>]                                                  |
| `batch_numbers`                                                                   | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"BATCH-2024-Q1-001",<br/>"BATCH-2024-Q1-002"<br/>]                          |
| `duration_min`                                                                    | *Optional[str]*                                                                   | :heavy_minus_sign:                                                                | N/A                                                                               | PT5M                                                                              |
| `duration_max`                                                                    | *Optional[str]*                                                                   | :heavy_minus_sign:                                                                | N/A                                                                               | PT30M                                                                             |
| `started_after`                                                                   | [date](https://docs.python.org/3/library/datetime.html#date-objects)              | :heavy_minus_sign:                                                                | N/A                                                                               | 2024-01-15T10:30:00Z                                                              |
| `started_before`                                                                  | [date](https://docs.python.org/3/library/datetime.html#date-objects)              | :heavy_minus_sign:                                                                | N/A                                                                               | 2024-01-15T11:30:00Z                                                              |
| `ended_after`                                                                     | [date](https://docs.python.org/3/library/datetime.html#date-objects)              | :heavy_minus_sign:                                                                | N/A                                                                               | 2024-01-15T10:30:00Z                                                              |
| `ended_before`                                                                    | [date](https://docs.python.org/3/library/datetime.html#date-objects)              | :heavy_minus_sign:                                                                | N/A                                                                               | 2024-01-15T11:30:00Z                                                              |
| `created_after`                                                                   | [date](https://docs.python.org/3/library/datetime.html#date-objects)              | :heavy_minus_sign:                                                                | N/A                                                                               | 2024-01-15T10:30:00Z                                                              |
| `created_before`                                                                  | [date](https://docs.python.org/3/library/datetime.html#date-objects)              | :heavy_minus_sign:                                                                | N/A                                                                               | 2024-01-15T11:30:00Z                                                              |
| `created_by_user_ids`                                                             | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                                |
| `created_by_station_ids`                                                          | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                                |
| `operated_by_ids`                                                                 | List[*str*]                                                                       | :heavy_minus_sign:                                                                | N/A                                                                               | [<br/>"550e8400-e29b-41d4-a716-446655440001"<br/>]                                |
| `limit`                                                                           | *Optional[int]*                                                                   | :heavy_minus_sign:                                                                | Maximum number of runs to return per page.                                        | 20                                                                                |
| `cursor`                                                                          | *Optional[float]*                                                                 | :heavy_minus_sign:                                                                | N/A                                                                               | 50                                                                                |
| `sort_by`                                                                         | [Optional[models.RunListSortBy]](../../models/runlistsortby.md)                   | :heavy_minus_sign:                                                                | Field to sort results by.                                                         | started_at                                                                        |
| `sort_order`                                                                      | [Optional[models.RunListSortOrder]](../../models/runlistsortorder.md)             | :heavy_minus_sign:                                                                | Sort order direction.                                                             | desc                                                                              |
| `retries`                                                                         | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                  | :heavy_minus_sign:                                                                | Configuration to override the default retry behavior of the client.               |                                                                                   |

### Response

**[models.RunListResponse](../../models/runlistresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## create

Create a new test run, linking it to a procedure and unit. Existing entities are reused automatically.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot
from tofupilot.v2.utils import parse_datetime


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.runs.create(outcome="PASS", procedure_id="550e8400-e29b-41d4-a716-446655440000", started_at=parse_datetime("2024-01-15T10:30:00Z"), ended_at=parse_datetime("2024-01-15T10:35:30Z"), serial_number="SN-001234", procedure_version="v1.2.3", operated_by="john.doe@example.com", part_number="PCB-V1.2", revision_number="REV-1.0", batch_number="BATCH-2024-01", sub_units=[
        "SUB-001",
        "SUB-002",
    ], docstring="Test run for production validation", phases=[
        {
            "name": "Power On Test",
            "outcome": "PASS",
            "started_at": parse_datetime("2024-01-15T10:30:00Z"),
            "ended_at": parse_datetime("2024-01-15T10:35:00Z"),
            "docstring": "Initial power-on sequence validation",
            "measurements": [
                {
                    "name": "Voltage Output",
                    "outcome": "PASS",
                    "measured_value": 3.3,
                    "units": "V",
                    "lower_limit": 3,
                    "upper_limit": 3.6,
                    "validators": [
                        "3.0 <= x <= 3.6",
                        "x is within 5% of 3.3",
                    ],
                    "docstring": "Main power rail voltage measurement after stabilization",
                },
            ],
        },
    ], logs=[
        {
            "level": "INFO",
            "timestamp": parse_datetime("2024-01-15T10:30:15Z"),
            "message": "Starting voltage measurement sequence",
            "source_file": "voltage_test.py",
            "line_number": 42,
        },
    ])

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                                                                                                                                                                                                                                                                    | Type                                                                                                                                                                                                                                                                                                                                         | Required                                                                                                                                                                                                                                                                                                                                     | Description                                                                                                                                                                                                                                                                                                                                  | Example                                                                                                                                                                                                                                                                                                                                      |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `outcome`                                                                                                                                                                                                                                                                                                                                    | [models.RunCreateOutcome](../../models/runcreateoutcome.md)                                                                                                                                                                                                                                                                                  | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                           | Overall test result. Use PASS when test succeeds, FAIL when test fails but script execution completed successfully, ERROR when script execution fails, TIMEOUT when test exceeds time limit, ABORTED for manual script interruption.                                                                                                         | PASS                                                                                                                                                                                                                                                                                                                                         |
| `procedure_id`                                                                                                                                                                                                                                                                                                                               | *str*                                                                                                                                                                                                                                                                                                                                        | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                           | Procedure ID. Create the procedure in the app first, then find the auto-generated ID on the procedure page.                                                                                                                                                                                                                                  | 550e8400-e29b-41d4-a716-446655440000                                                                                                                                                                                                                                                                                                         |
| `started_at`                                                                                                                                                                                                                                                                                                                                 | [date](https://docs.python.org/3/library/datetime.html#date-objects)                                                                                                                                                                                                                                                                         | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                           | ISO 8601 timestamp when the test run began execution. This timestamp will be used to track when the test execution started and for historical analysis of test runs. A separate created_at timestamp is stored internally server side to track upload date.                                                                                  | 2024-01-15T10:30:00Z                                                                                                                                                                                                                                                                                                                         |
| `ended_at`                                                                                                                                                                                                                                                                                                                                   | [date](https://docs.python.org/3/library/datetime.html#date-objects)                                                                                                                                                                                                                                                                         | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                           | ISO 8601 timestamp when the test run finished execution.                                                                                                                                                                                                                                                                                     | 2024-01-15T10:35:30Z                                                                                                                                                                                                                                                                                                                         |
| `serial_number`                                                                                                                                                                                                                                                                                                                              | *str*                                                                                                                                                                                                                                                                                                                                        | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                           | Unique serial number of the unit under test. Matched case-insensitively. If no unit with this serial number exists, one will be created.                                                                                                                                                                                                     | SN-001234                                                                                                                                                                                                                                                                                                                                    |
| `procedure_version`                                                                                                                                                                                                                                                                                                                          | *OptionalNullable[str]*                                                                                                                                                                                                                                                                                                                      | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | N/A                                                                                                                                                                                                                                                                                                                                          | v1.2.3                                                                                                                                                                                                                                                                                                                                       |
| `operated_by`                                                                                                                                                                                                                                                                                                                                | *Optional[str]*                                                                                                                                                                                                                                                                                                                              | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | Email address of the operator who executed the test run. The operator must exist as a user in the system. The run will be linked to this user to track who performed the test.                                                                                                                                                               | john.doe@example.com                                                                                                                                                                                                                                                                                                                         |
| `part_number`                                                                                                                                                                                                                                                                                                                                | *Optional[str]*                                                                                                                                                                                                                                                                                                                              | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | Component part number for the unit. Matched case-insensitively. This field is required if the part number cannot be extracted from the serial number (as set in the settings). This field takes precedence over extraction from serial number. A component with the provided or extracted part number will be created if one does not exist. | PCB-V1.2                                                                                                                                                                                                                                                                                                                                     |
| `revision_number`                                                                                                                                                                                                                                                                                                                            | *Optional[str]*                                                                                                                                                                                                                                                                                                                              | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | Hardware revision identifier for the unit. Matched case-insensitively. If none exist, a revision with this number will be created. If no revision is specified, the unit will be linked to the default revision of the part number.                                                                                                          | REV-1.0                                                                                                                                                                                                                                                                                                                                      |
| `batch_number`                                                                                                                                                                                                                                                                                                                               | *Optional[str]*                                                                                                                                                                                                                                                                                                                              | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | Production batch identifier for grouping units manufactured together. Matched case-insensitively. If none exist, a batch with this batch number will be created. If no batch number is specified, the unit will not be linked to any batch.                                                                                                  | BATCH-2024-01                                                                                                                                                                                                                                                                                                                                |
| `sub_units`                                                                                                                                                                                                                                                                                                                                  | List[*str*]                                                                                                                                                                                                                                                                                                                                  | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | Array of sub-unit serial numbers that are part of this main unit. Matched case-insensitively. Each sub-unit must already exist and will be linked as a sub-component of the main unit under test. If no sub-units are specified, the unit will be created without sub-unit relationships.                                                    | [<br/>"SUB-001",<br/>"SUB-002"<br/>]                                                                                                                                                                                                                                                                                                         |
| `docstring`                                                                                                                                                                                                                                                                                                                                  | *Optional[str]*                                                                                                                                                                                                                                                                                                                              | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | Additional notes or documentation about this test run.                                                                                                                                                                                                                                                                                       | Test run for production validation                                                                                                                                                                                                                                                                                                           |
| `phases`                                                                                                                                                                                                                                                                                                                                     | List[[models.RunCreatePhase](../../models/runcreatephase.md)]                                                                                                                                                                                                                                                                                | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | Array of test phases with measurements and results. Each phase represents a distinct stage of the test execution with timing information, outcome status, and optional measurements. If no phases are specified, the run will be created without phase-level organization of test data.                                                      |                                                                                                                                                                                                                                                                                                                                              |
| `logs`                                                                                                                                                                                                                                                                                                                                       | List[[models.RunCreateLog](../../models/runcreatelog.md)]                                                                                                                                                                                                                                                                                    | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | Array of log messages generated during the test execution. Each log entry captures events, errors, and diagnostic information with severity levels and source code references. If no logs are specified, the run will be created without log entries.                                                                                        |                                                                                                                                                                                                                                                                                                                                              |
| `retries`                                                                                                                                                                                                                                                                                                                                    | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                                                                                                                                                                                                                                             | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                           | Configuration to override the default retry behavior of the client.                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                                                                                              |

### Response

**[models.RunCreateResponse](../../models/runcreateresponse.md)**

### Errors

| Error Type                       | Status Code                      | Content Type                     |
| -------------------------------- | -------------------------------- | -------------------------------- |
| errors.ErrorBADREQUEST           | 400                              | application/json                 |
| errors.ErrorUNAUTHORIZED         | 401                              | application/json                 |
| errors.ErrorFORBIDDEN            | 403                              | application/json                 |
| errors.ErrorNOTFOUND             | 404                              | application/json                 |
| errors.ErrorUNPROCESSABLECONTENT | 422                              | application/json                 |
| errors.ErrorINTERNALSERVERERROR  | 500                              | application/json                 |
| errors.APIError                  | 4XX, 5XX                         | \*/\*                            |

## delete

Permanently delete test runs by their IDs. Removes all associated phases, measurements, and attachments.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.runs.delete(ids=[
        "550e8400-e29b-41d4-a716-446655440000",
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    ])

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        | Example                                                                            |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `ids`                                                                              | List[*str*]                                                                        | :heavy_check_mark:                                                                 | Run IDs to delete.                                                                 | [<br/>"550e8400-e29b-41d4-a716-446655440000",<br/>"6ba7b810-9dad-11d1-80b4-00c04fd430c8"<br/>] |
| `retries`                                                                          | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                   | :heavy_minus_sign:                                                                 | Configuration to override the default retry behavior of the client.                |                                                                                    |

### Response

**[models.RunDeleteResponse](../../models/rundeleteresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## get

Retrieve a single test run by its ID. Returns comprehensive run data including metadata, phases, measurements, and logs.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.runs.get(id="550e8400-e29b-41d4-a716-446655440000")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `id`                                                                | *str*                                                               | :heavy_check_mark:                                                  | ID of the run to retrieve.                                          |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.RunGetResponse](../../models/rungetresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## update

Update a test run, including linking file attachments. Files must be uploaded via Initialize upload and Finalize upload before linking.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.runs.update(id="550e8400-e29b-41d4-a716-446655440000", attachments=[
        "550e8400-e29b-41d4-a716-446655440000",
    ])

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `id`                                                                | *str*                                                               | :heavy_check_mark:                                                  | Unique identifier of the run to update.                             |                                                                     |
| `attachments`                                                       | List[*str*]                                                         | :heavy_minus_sign:                                                  | Array of upload IDs to attach to the run.                           | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                  |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.RunUpdateResponse](../../models/runupdateresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |