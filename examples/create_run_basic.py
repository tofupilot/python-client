"""
Basic example showing how to create a test run using the TofuPilotClient.

This script creates a test run for a unit with the specified serial number and part number,
indicating whether the test passed.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""

from tofupilot import TofuPilotClient

# Initialize the TofuPilot client.
client = TofuPilotClient()

# Create a test run for the unit with serial number "00102" and part number "PCB01"
response = client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
    run_passed=True,
)

# Ensure the run was successfully created
success = response.get("success")

assert success
