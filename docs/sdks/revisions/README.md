# Revisions
(*parts.revisions*)

## Overview

### Available Operations

* [get](#get) - Get part revision
* [delete](#delete) - Delete part revision
* [update](#update) - Update part revision
* [create](#create) - Create part revision

## get

Retrieve a single part revision by its part number and revision number, including revision metadata, configuration details, and linked units.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.parts.revisions.get(part_number="PCB-V2.0", revision_number="REV-A")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `part_number`                                                       | *str*                                                               | :heavy_check_mark:                                                  | Part number that the revision belongs to.                           |
| `revision_number`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Revision number to retrieve.                                        |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.PartGetRevisionResponse](../../models/partgetrevisionresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## delete

Permanently delete a part revision by its part number and revision number. This action removes the revision and all associated data and cannot be undone.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.parts.revisions.delete(part_number="PCB-V2.0", revision_number="REV-A")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `part_number`                                                       | *str*                                                               | :heavy_check_mark:                                                  | Part number that the revision belongs to.                           |
| `revision_number`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Revision number to delete.                                          |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.PartDeleteRevisionResponse](../../models/partdeleterevisionresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## update

Update a part revision's number or image. Identifies the revision by part number and revision number in the URL.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.parts.revisions.update(part_number="<value>", revision_number="<value>", number="REV-B")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `part_number`                                                       | *str*                                                               | :heavy_check_mark:                                                  | Part number that the revision belongs to.                           |                                                                     |
| `revision_number`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Current revision number to update.                                  |                                                                     |
| `number`                                                            | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | New revision number to set.                                         | REV-B                                                               |
| `image_id`                                                          | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | Upload ID for the revision image, or empty string to remove image   |                                                                     |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.PartUpdateRevisionResponse](../../models/partupdaterevisionresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## create

Create a new part revision for an existing part. Revision numbers are matched case-insensitively (e.g., "REV-A" and "rev-a" are considered the same).

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.parts.revisions.create(part_number="PCB-MAIN-001", number="REV-A")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `part_number`                                                       | *str*                                                               | :heavy_check_mark:                                                  | Part number to create a revision for.                               |                                                                     |
| `number`                                                            | *str*                                                               | :heavy_check_mark:                                                  | Revision number (e.g., version number or code).                     | REV-A                                                               |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |                                                                     |

### Response

**[models.PartCreateRevisionResponse](../../models/partcreaterevisionresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorCONFLICT            | 409                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |