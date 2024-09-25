"""
Example script demonstrating how to create a test run using the TofuPilotClient with 
a custom test function, including the measurement of test duration, report variables, 
and attachments.

This script runs a test, measures its duration, and then creates a test run in TofuPilot, 
indicating whether the test passed, and including relevant report variables and attachments.

Ensure your API key is stored in the environment variables as per the documentation:
https://docs.tofupilot.com/user-management#api-key
"""

import time
from datetime import datetime
from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()


def test_function():
    """
    Simulates a test execution, including setting pass/fail status,
    report variables, and attachments.
    """
    # Simulate test execution with a delay
    time.sleep(1)

    # Define test results and related data
    run_passed = True
    report_variables = {
        "initial_temperature_reading": "72°C",
        "final_temperature_reading": "75°C",
    }
    attachments = ["data/temperature-map.png", "data/performance-report.pdf"]

    return run_passed, report_variables, attachments


# Measure the duration of the test_function
start_time = datetime.now()
run_passed, report_variables, attachments = test_function()
end_time = datetime.now()
duration = end_time - start_time

# Create a test run in TofuPilot with the results from test_function
response = client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
    run_passed=run_passed,
    duration=duration,
    report_variables=report_variables,
    attachments=attachments,
)

# Ensure the run was successfully created
success = response.get("success")

assert success
