"""
Example script demonstrating how to create a test run in TofuPilot by uploading
test results from a report file.

This script uploads a test report in JSON format to TofuPilot using the specified 
importer type. Currently, "OPENHTF" is the only available importer, but support 
for additional importers is coming soon.

Ensure your API key is stored in the environment variables as per the documentation:
https://docs.tofupilot.com/user-management#api-key
"""

from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()

# Path to the test report file
file_path = "data/simple_openhtf_report.json"

# Upload the test results to TofuPilot, specifying the importer type
response = client.create_run_from_report(file_path, importer="OPENHTF")

# Ensure the run was successfully created
success = response.get("success")

assert success
