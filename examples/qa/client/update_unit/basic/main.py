"""
Simple example showing how to add a sub-unit to an existing unit using the TofuPilotClient.

This script assumes you already have two units with the respective serial numbers "00102" and "00103".
If the units do not exist, you can uncomment the lines to create them first.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""

from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()

# Creating units
client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
    run_passed=True,
)
client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00103", "part_number": "PSU01"},
    run_passed=True,
)

# Update unit "00102" by adding unit "00103" as a sub-unit
client.update_unit(serial_number="00102",
                   sub_units=[{"serial_number": "00103"}])
