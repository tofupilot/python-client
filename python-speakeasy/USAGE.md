<!-- Start SDK Example Usage [usage] -->
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