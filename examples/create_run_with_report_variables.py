"""
Example script demonstrating how to create a test run in TofuPilot with report variables.

This script creates a test run for a unit with the specified serial number and part number,
and includes additional report variables such as temperature readings, calibration date, 
and technician information.

Ensure your API key is stored in the environment variables as per the documentation:
https://docs.tofupilot.com/user-management#api-key
"""

from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()

# Create a test run for the unit with serial number "0001" and part number "PCB01",
# including detailed report variables
response = client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "0001", "part_number": "PCB01"},
    run_passed=True,
    report_variables={
        "temperature_sensor": "75°C",
        "calibration_date": "2024-06-20",
        "technician_name": "John Doe",
        "initial_temperature_reading": "72°C",
        "final_temperature_reading": "75°C",
    },
)

# Ensure the run was successfully created
success = response.get("success")

assert success
