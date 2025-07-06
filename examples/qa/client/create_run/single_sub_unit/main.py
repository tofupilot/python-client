"""
Example script demonstrating how to create a test run in TofuPilot with a single sub-unit.

This script creates a test run for a unit with the specified serial number and part number,
and includes a single sub-unit in the run.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""

from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()

# Create a test run for the unit with serial number "00002" and part number "SI001",
# including a sub-unit with serial number "00102"
client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00002", "part_number": "SI001"},
    run_passed=True,
    sub_units=[{"serial_number": "00102"}],
)
