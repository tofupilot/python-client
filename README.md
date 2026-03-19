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
