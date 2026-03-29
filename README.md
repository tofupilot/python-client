# TofuPilot Python Client

[![PyPI version](https://badge.fury.io/py/tofupilot.svg)](https://badge.fury.io/py/tofupilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official open-source Python client for [TofuPilot](https://tofupilot.com). Integrate your hardware test runs into one app with just a few lines of Python.

## Installation

```bash
pip install tofupilot
```

## Quick Start

```python
import os
from tofupilot.v2 import TofuPilot

with TofuPilot(api_key=os.getenv("TOFUPILOT_API_KEY")) as client:
    client.runs.create(
        procedure_id="FVT1",
        serial_number="SN001",
        part_number="PN001",
        outcome="PASS",
    )
```

## Documentation

- [Getting Started](https://tofupilot.com/docs/dashboard)
- [API Reference](https://tofupilot.com/docs/dashboard/api/v2)
- [Changelog](https://tofupilot.com/changelog)

## Authentication

Set your API key as an environment variable:

```bash
export TOFUPILOT_API_KEY="your-api-key"
```

Or pass it directly when initializing the client.

## Contributing

Please read [CONTRIBUTING](https://github.com/tofupilot/python-client/blob/main/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

MIT - see [LICENSE](https://github.com/tofupilot/python-client/blob/main/LICENSE) for details.

<!-- Start Summary [summary] -->
## Summary

TofuPilot APIv2: TofuPilot REST API for managing runs, units, procedures, and more.

More information about the API can be found at https://tofupilot.com/docs/dashboard/api/v2/runs/create
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [TofuPilot Python Client](#tofupilot-python-client)
  * [Installation](#installation)
  * [Quick Start](#quick-start)
  * [Documentation](#documentation)
  * [Authentication](#authentication)
  * [Contributing](#contributing)
  * [License](#license)
  * [SDK Installation](#sdk-installation)
  * [IDE Support](#ide-support)
  * [SDK Example Usage](#sdk-example-usage)
  * [Authentication](#authentication-1)
  * [Available Resources and Operations](#available-resources-and-operations)
  * [Retries](#retries)
  * [Error Handling](#error-handling)
  * [Server Selection](#server-selection)
  * [Custom HTTP Client](#custom-http-client)
  * [Resource Management](#resource-management)
  * [Debugging](#debugging)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!TIP]
> To finish publishing your SDK to PyPI you must [run your first generation action](https://www.speakeasy.com/docs/github-setup#step-by-step-guide).


> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with either *pip* or *poetry* package managers.

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install git+<UNSET>.git
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add git+<UNSET>.git
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from tofupilot.v2 python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "tofupilot.v2",
# ]
# ///

from tofupilot.v2 import TofuPilot

sdk = TofuPilot(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.
<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
# Synchronous Example
import os
from tofupilot.v2 import TofuPilot
from tofupilot.v2.utils import parse_datetime


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.procedures.list(limit=20, cursor=50, search_query="battery test", created_after=parse_datetime("2024-01-01T00:00:00.000Z"), created_before=parse_datetime("2024-12-31T23:59:59.999Z"))

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
import os
from tofupilot.v2 import TofuPilot
from tofupilot.v2.utils import parse_datetime

async def main():

    async with TofuPilot(
        api_key=os.getenv("TOFUPILOT_API_KEY", ""),
    ) as tofu_pilot:

        res = await tofu_pilot.procedures.list_async(limit=20, cursor=50, search_query="battery test", created_after=parse_datetime("2024-01-01T00:00:00.000Z"), created_before=parse_datetime("2024-12-31T23:59:59.999Z"))

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name      | Type | Scheme      | Environment Variable |
| --------- | ---- | ----------- | -------------------- |
| `api_key` | http | HTTP Bearer | `TOFUPILOT_API_KEY`  |

To authenticate with the API the `api_key` parameter must be set when initializing the SDK client instance. For example:
```python
import os
from tofupilot.v2 import TofuPilot
from tofupilot.v2.utils import parse_datetime


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.procedures.list(limit=20, cursor=50, search_query="battery test", created_after=parse_datetime("2024-01-01T00:00:00.000Z"), created_before=parse_datetime("2024-12-31T23:59:59.999Z"))

    # Handle response
    print(res)

```
<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [attachments](docs/sdks/attachments/README.md)

* [initialize](docs/sdks/attachments/README.md#initialize) - Initialize upload
* [delete](docs/sdks/attachments/README.md#delete) - Delete attachments
* [finalize](docs/sdks/attachments/README.md#finalize) - Finalize upload

### [batches](docs/sdks/batches/README.md)

* [get](docs/sdks/batches/README.md#get) - Get batch
* [delete](docs/sdks/batches/README.md#delete) - Delete batch
* [update](docs/sdks/batches/README.md#update) - Update batch
* [list](docs/sdks/batches/README.md#list) - List and filter batches
* [create](docs/sdks/batches/README.md#create) - Create batch

### [parts](docs/sdks/parts/README.md)

* [list](docs/sdks/parts/README.md#list) - List and filter parts
* [create](docs/sdks/parts/README.md#create) - Create part
* [get](docs/sdks/parts/README.md#get) - Get part
* [delete](docs/sdks/parts/README.md#delete) - Delete part
* [update](docs/sdks/parts/README.md#update) - Update part

#### [parts.revisions](docs/sdks/revisions/README.md)

* [get](docs/sdks/revisions/README.md#get) - Get part revision
* [delete](docs/sdks/revisions/README.md#delete) - Delete part revision
* [update](docs/sdks/revisions/README.md#update) - Update part revision
* [create](docs/sdks/revisions/README.md#create) - Create part revision

### [procedures](docs/sdks/procedures/README.md)

* [list](docs/sdks/procedures/README.md#list) - List and filter procedures
* [create](docs/sdks/procedures/README.md#create) - Create procedure
* [get](docs/sdks/procedures/README.md#get) - Get procedure
* [delete](docs/sdks/procedures/README.md#delete) - Delete procedure
* [update](docs/sdks/procedures/README.md#update) - Update procedure

#### [procedures.versions](docs/sdks/versions/README.md)

* [get](docs/sdks/versions/README.md#get) - Get procedure version
* [delete](docs/sdks/versions/README.md#delete) - Delete procedure version
* [create](docs/sdks/versions/README.md#create) - Create procedure version

### [runs](docs/sdks/runs/README.md)

* [list](docs/sdks/runs/README.md#list) - List and filter runs
* [create](docs/sdks/runs/README.md#create) - Create run
* [delete](docs/sdks/runs/README.md#delete) - Delete runs
* [get](docs/sdks/runs/README.md#get) - Get run
* [update](docs/sdks/runs/README.md#update) - Update run

### [stations](docs/sdks/stations/README.md)

* [list](docs/sdks/stations/README.md#list) - List and filter stations
* [create](docs/sdks/stations/README.md#create) - Create station
* [get_current](docs/sdks/stations/README.md#get_current) - Get current station
* [get](docs/sdks/stations/README.md#get) - Get station
* [remove](docs/sdks/stations/README.md#remove) - Remove station
* [update](docs/sdks/stations/README.md#update) - Update station


### [units](docs/sdks/unitssdk/README.md)

* [list](docs/sdks/unitssdk/README.md#list) - List and filter units
* [create](docs/sdks/unitssdk/README.md#create) - Create unit
* [delete](docs/sdks/unitssdk/README.md#delete) - Delete units
* [get](docs/sdks/unitssdk/README.md#get) - Get unit
* [update](docs/sdks/unitssdk/README.md#update) - Update unit
* [add_child](docs/sdks/unitssdk/README.md#add_child) - Add sub-unit
* [remove_child](docs/sdks/unitssdk/README.md#remove_child) - Remove sub-unit

### [user](docs/sdks/user/README.md)

* [list](docs/sdks/user/README.md#list) - List users

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
import os
from tofupilot.v2 import TofuPilot
from tofupilot.v2.utils import BackoffStrategy, RetryConfig, parse_datetime


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.procedures.list(limit=20, cursor=50, search_query="battery test", created_after=parse_datetime("2024-01-01T00:00:00.000Z"), created_before=parse_datetime("2024-12-31T23:59:59.999Z"),
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
import os
from tofupilot.v2 import TofuPilot
from tofupilot.v2.utils import BackoffStrategy, RetryConfig, parse_datetime


with TofuPilot(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.procedures.list(limit=20, cursor=50, search_query="battery test", created_after=parse_datetime("2024-01-01T00:00:00.000Z"), created_before=parse_datetime("2024-12-31T23:59:59.999Z"))

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

[`TofuPilotError`](./src/tofupilot/v2/errors/tofupiloterror.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](#error-classes). |

### Example
```python
import os
from tofupilot.v2 import TofuPilot, errors
from tofupilot.v2.utils import parse_datetime


with TofuPilot(
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:
    res = None
    try:

        res = tofu_pilot.procedures.list(limit=20, cursor=50, search_query="battery test", created_after=parse_datetime("2024-01-01T00:00:00.000Z"), created_before=parse_datetime("2024-12-31T23:59:59.999Z"))

        # Handle response
        print(res)


    except errors.TofuPilotError as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, errors.ErrorBADREQUEST):
            print(e.data.message)  # str
            print(e.data.code)  # str
            print(e.data.issues)  # Optional[List[models.ErrorBADREQUESTIssue]]
```

### Error Classes
**Primary errors:**
* [`TofuPilotError`](./src/tofupilot/v2/errors/tofupiloterror.py): The base class for HTTP error responses.
  * [`ErrorUNAUTHORIZED`](./src/tofupilot/v2/errors/errorunauthorized.py): Unauthorized error. Status code `401`.
  * [`ErrorINTERNALSERVERERROR`](./src/tofupilot/v2/errors/errorinternalservererror.py): Internal server error error. Status code `500`.

<details><summary>Less common errors (11)</summary>

<br />

**Network errors:**
* [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
    * [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
    * [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.


**Inherit from [`TofuPilotError`](./src/tofupilot/v2/errors/tofupiloterror.py)**:
* [`ErrorNOTFOUND`](./src/tofupilot/v2/errors/errornotfound.py): Not found error. Status code `404`. Applicable to 32 of 44 methods.*
* [`ErrorBADREQUEST`](./src/tofupilot/v2/errors/errorbadrequest.py): Bad request error. Status code `400`. Applicable to 15 of 44 methods.*
* [`ErrorCONFLICT`](./src/tofupilot/v2/errors/errorconflict.py): Conflict error. Status code `409`. Applicable to 12 of 44 methods.*
* [`ErrorFORBIDDEN`](./src/tofupilot/v2/errors/errorforbidden.py): Forbidden error. Status code `403`. Applicable to 4 of 44 methods.*
* [`ErrorUNPROCESSABLECONTENT`](./src/tofupilot/v2/errors/errorunprocessablecontent.py): Unprocessable content error. Status code `422`. Applicable to 1 of 44 methods.*
* [`ErrorBADGATEWAY`](./src/tofupilot/v2/errors/errorbadgateway.py): Bad gateway error. Status code `502`. Applicable to 1 of 44 methods.*
* [`ResponseValidationError`](./src/tofupilot/v2/errors/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>

\* Check [the method documentation](#available-resources-and-operations) to see if the error is applicable.
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
import os
from tofupilot.v2 import TofuPilot
from tofupilot.v2.utils import parse_datetime


with TofuPilot(
    server_url="https://www.tofupilot.app/api",
    api_key=os.getenv("TOFUPILOT_API_KEY", ""),
) as tofu_pilot:

    res = tofu_pilot.procedures.list(limit=20, cursor=50, search_query="battery test", created_after=parse_datetime("2024-01-01T00:00:00.000Z"), created_before=parse_datetime("2024-12-31T23:59:59.999Z"))

    # Handle response
    print(res)

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from tofupilot.v2 import TofuPilot
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = TofuPilot(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from tofupilot.v2 import TofuPilot
from tofupilot.v2.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = TofuPilot(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `TofuPilot` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
import os
from tofupilot.v2 import TofuPilot
def main():

    with TofuPilot(
        api_key=os.getenv("TOFUPILOT_API_KEY", ""),
    ) as tofu_pilot:
        # Rest of application here...


# Or when using async:
async def amain():

    async with TofuPilot(
        api_key=os.getenv("TOFUPILOT_API_KEY", ""),
    ) as tofu_pilot:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from tofupilot.v2 import TofuPilot
import logging

logging.basicConfig(level=logging.DEBUG)
s = TofuPilot(debug_logger=logging.getLogger("tofupilot.v2"))
```

You can also enable a default debug logger by setting an environment variable `TOFUPILOT_DEBUG` to true.
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->
