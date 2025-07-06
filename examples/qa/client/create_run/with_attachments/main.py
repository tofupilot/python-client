"""
Example script demonstrating how to create a test run in TofuPilot with attachments.

This script creates a test run for a unit with the specified serial number and part number,
and includes attachments, such as images and reports, that are related to the test.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""

from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()

# Create a test run for the unit with serial number "00102" and part number "PCB01",
# including attachments such as images and PDF reports
client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
    run_passed=True,
    attachments=[
        "data/temperature-map.png",  # Path to your local files
        "data/performance-report.pdf",
    ],
)
