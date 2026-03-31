# Attachments
(*attachments*)

## Overview

### Available Operations

* [initialize](#initialize) - Initialize upload
* [delete](#delete) - Delete attachments
* [finalize](#finalize) - Finalize upload

## initialize

Get a temporary pre-signed URL to upload a file. Returns the upload ID and URL. Upload the file to the URL with a PUT request, then call Finalize upload.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.attachments.initialize(name="<value>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `name`                                                              | *str*                                                               | :heavy_check_mark:                                                  | File name including extension (e.g. "report.pdf")                   |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.AttachmentInitializeResponse](../../models/attachmentinitializeresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorFORBIDDEN           | 403                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.ErrorBADGATEWAY          | 502                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## delete

Permanently delete attachments by their IDs and unlink them from any associated runs or units.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.attachments.delete(ids=[
        "550e8400-e29b-41d4-a716-446655440000",
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    ])

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        | Example                                                                            |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `ids`                                                                              | List[*str*]                                                                        | :heavy_check_mark:                                                                 | Upload IDs to delete                                                               | [<br/>"550e8400-e29b-41d4-a716-446655440000",<br/>"6ba7b810-9dad-11d1-80b4-00c04fd430c8"<br/>] |
| `retries`                                                                          | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                   | :heavy_minus_sign:                                                                 | Configuration to override the default retry behavior of the client.                |                                                                                    |

### Response

**[models.AttachmentDeleteResponse](../../models/attachmentdeleteresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorBADREQUEST          | 400                             | application/json                |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |

## finalize

Finalize a file upload after uploading to the pre-signed URL. Validates the file and records its metadata. Link the attachment to a run or unit using Update Run or Update Unit.

### Example Usage

```python
import os
from tofupilot.v2 import TofuPilot


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.attachments.finalize(id="<id>", request_body={})

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                             | Type                                                                                  | Required                                                                              | Description                                                                           |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `id`                                                                                  | *str*                                                                                 | :heavy_check_mark:                                                                    | ID of the upload to finalize                                                          |
| `request_body`                                                                        | [models.AttachmentFinalizeRequestBody](../../models/attachmentfinalizerequestbody.md) | :heavy_check_mark:                                                                    | N/A                                                                                   |
| `retries`                                                                             | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                      | :heavy_minus_sign:                                                                    | Configuration to override the default retry behavior of the client.                   |

### Response

**[models.AttachmentFinalizeResponse](../../models/attachmentfinalizeresponse.md)**

### Errors

| Error Type                      | Status Code                     | Content Type                    |
| ------------------------------- | ------------------------------- | ------------------------------- |
| errors.ErrorUNAUTHORIZED        | 401                             | application/json                |
| errors.ErrorNOTFOUND            | 404                             | application/json                |
| errors.ErrorINTERNALSERVERERROR | 500                             | application/json                |
| errors.APIError                 | 4XX, 5XX                        | \*/\*                           |