# TofuPilot Python client

The official Python client for [TofuPilot](https://tofupilot.com).
Quickly and seemlessly integrate all your hardware test runs into one app by using this powerful open-source client.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

Package can be installed via pip

```bash
pip install tofupilot
```

## Usage

A test run can be easily created in TofuPilot using a few parameters.

```python
from tofupilot import TofuPilotClient
import time
from datetime import timedelta

client = TofuPilotClient(api_key="Your API key goes here")

def test_function():
    # Your test execution goes here
    time.sleep(1)  # Placeholder for test execution time
    return True

# Measure the duration of the test_function (optional)
start_time = time.time()
run_passed = test_function()
end_time = time.time()
duration = end_time - start_time

client.create_run(
    procedure_id="FVT1",
    unit_under_test={
      "serial_number": "00102",
      "part_number": "PCB01"
    },
    run_passed=run_passed,
    duration=timedelta(seconds=end_time-start_time) # Optional argument
)
```

# Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

# License

This project is licensed under the MIT License - see the LICENSE.md file for details.

# Contact

If you have any questions or feedback, feel free to open an issue or contact us at support@tofupilot.com.
