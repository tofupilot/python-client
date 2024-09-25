from tofupilot import TofuPilotClient

client = TofuPilotClient()


response = client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00002", "part_number": "SI001"},
    run_passed=True,
    sub_units=[{"serial_number": "00102"}],
)

success = response.get("success")

assert success
