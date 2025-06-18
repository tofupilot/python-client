"""
Example script demonstrating how to create and then fetch a test run in TofuPilot.

This script first creates a test run for a unit with a specified serial number and part number,
then retrieves the run data using the serial number.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""

from tofupilot import TofuPilotClient
import json

# Initialize the TofuPilot client
client = TofuPilotClient()

# Define the serial number of the unit under test
serial_number = "SN00106"

client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": serial_number, "part_number": "PCB01"},
    run_passed=True,
)

# Fetch the created run using the serial number
response = client.get_runs(serial_number=serial_number)


# Save JSON response locally
with open("response_saved.json", "w") as f:
    json.dump(response, f, indent=2)

print("Response saved to response_saved.json")
