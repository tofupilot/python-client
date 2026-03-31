# Stations
(*stations*)

## Overview

### Available Operations

* [list](#list) - List and filter stations
* [create](#create) - Create station
* [get_current](#get_current) - Get current station
* [get](#get) - Get station
* [remove](#remove) - Remove station
* [update](#update) - Update station

## list

Retrieve a paginated list of test stations in your organization. Search by station name and filter by status for station fleet management.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.stations.list(limit=50, cursor=1, search_query="assembly", procedure_ids=[
        "550e8400-e29b-41d4-a716-446655440000",
    ])

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `limit`                                                             | *Optional[int]*                                                     | :heavy_minus_sign:                                                  | Number of stations to return per page                               | 50                                                                  |
| `cursor`                                                            | *Optional[int]*                                                     | :heavy_minus_sign:                                                  | N/A                                                                 | 1                                                                   |
| `search_query`                                                      | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | N/A                                                                 | assembly                                                            |
| `procedure_ids`                                                     | List[*str*]                                                         | :heavy_minus_sign:                                                  | N/A                                                                 | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>]                  |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.StationListResponse](../../models/stationlistresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## create

Create a new test station in TofuPilot to register production equipment and link it to test procedures.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.stations.create(name="Assembly Station 1", procedure_id="550e8400-e29b-41d4-a716-446655440000")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `name`                                                              | *str*                                                               | :heavy_check_mark:                                                  | Name of the station                                                 | Assembly Station 1                                                  |
| `procedure_id`                                                      | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | Optional procedure ID to link the station to                        | 550e8400-e29b-41d4-a716-446655440000                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.StationCreateResponse](../../models/stationcreateresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorFORBIDDEN           | 403                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## get_current

Retrieve detailed information about the currently authenticated station including linked procedures and connection status.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.stations.get_current()

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.StationGetCurrentResponse](../../models/stationgetcurrentresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorFORBIDDEN           | 403                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## get

Retrieve detailed station information including linked procedures, connection status, and recent activity.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.stations.get(id="550e8400-e29b-41d4-a716-446655440000")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `id`                                                                | *str*                                                               | :heavy_check_mark:                                                  | Unique identifier of the station to retrieve                        |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.StationGetResponse](../../models/stationgetresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## remove

Remove a test station. Deletes permanently if unused, or archives with preserved historical data if runs exist.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.stations.remove(id="550e8400-e29b-41d4-a716-446655440000")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `id`                                                                | *str*                                                               | :heavy_check_mark:                                                  | Unique identifier of the station to remove                          |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.StationRemoveResponse](../../models/stationremoveresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## update

Update station name and/or image. The station ID is specified in the URL path. To remove an image, pass an empty string for image_id.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.stations.update(id="550e8400-e29b-41d4-a716-446655440000", name="Assembly Station 2", team_id="550e8400-e29b-41d4-a716-446655440002")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `id`                                                                | *str*                                                               | :heavy_check_mark:                                                  | Unique identifier of the station to update                          |                                                                     |
| `name`                                                              | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | New name for the station                                            | Assembly Station 2                                                  |
| `image_id`                                                          | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | Upload ID for the station image, or empty string to remove image    |                                                                     |
| `team_id`                                                           | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Team ID to assign this station to, or null to unassign              | 550e8400-e29b-41d4-a716-446655440002                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.StationUpdateResponse](../../models/stationupdateresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |