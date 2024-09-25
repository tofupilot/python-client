from tofupilot import TofuPilotClient

# Initialize the TofuPilot client
client = TofuPilotClient()

serial_number = "00102"

# Creating a run
client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": serial_number, "part_number": "PCB01"},
    run_passed=True,
)


# Fetching it
response = client.get_runs(serial_number=serial_number)

data = response.get("data")

assert data is not None
