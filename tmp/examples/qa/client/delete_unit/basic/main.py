from tofupilot import TofuPilotClient

client = TofuPilotClient()

response = client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "NEW_UNIT", "part_number": "PCB01"},
    run_passed=True,
)

run_id = response.get("id")

client.delete_run(run_id=run_id)

client.delete_unit(serial_number="NEW_UNIT")
