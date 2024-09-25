from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()

file_path = "data/simple_openhtf_report.json"


# Upload the test results to TofuPilot, specifying the importer type
response = client.create_run_from_report(file_path, importer="OPENHTF")


success = response.get("success")

assert success
