"""
Example script demonstrating how to create a test run in TofuPilot with multiple sub-units.

This script creates a test run for a unit with the specified serial number and part number,
and includes multiple sub-units in the run.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""

from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()

# Create a test run for the unit with serial number "00003" and part number "SI002",
# including sub-units with serial numbers "00002" and "00102"
client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00003", "part_number": "SI002"},
    run_passed=True,
    sub_units=[{"serial_number": "00002"}, {"serial_number": "00102"}],
)
