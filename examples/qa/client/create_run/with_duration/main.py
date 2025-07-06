"""
Example script demonstrating how to create a test run in TofuPilot with the duration of the test.

This script measures the duration of a test function, then creates a test run for a unit
with the specified serial number and part number, including the duration as part of the run data.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""

import time
from datetime import timedelta

from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()


def test_function():
    """
    Simulates a test execution.
    """
    # Simulate test execution with a delay
    time.sleep(1)  # Placeholder for test execution time
    return True


# Measure the duration of the test_function
start_time = time.time()
run_passed = test_function()
end_time = time.time()
duration = timedelta(seconds=end_time - start_time)  # Calculate duration

# Create a test run for the unit with serial number "00102" and part number "PCB01",
# including the duration of the test
client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
    run_passed=run_passed,
    duration=duration,  # Optional argument to include the duration
)
