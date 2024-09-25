"""
Example script demonstrating how to create and then fetch a test run in TofuPilot.

This script first creates a test run for a unit with a specified serial number and part number,
then retrieves the run data using the serial number.

Ensure your API key is stored in the environment variables as per the documentation:
https://docs.tofupilot.com/user-management#api-key
"""

from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()

# Define the serial number of the unit under test
serial_number = "00102"

# Create a test run for the unit with serial number "00102" and part number "PCB01"
client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": serial_number, "part_number": "PCB01"},
    run_passed=True,
)

# Fetch the created run using the serial number
response = client.get_runs(serial_number=serial_number)

# Extract the data from the response
data = response.get("data")

# Ensure that the run data was successfully retrieved
assert data is not None
