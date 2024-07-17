from tofupilot import TofuPilotClient

client = TofuPilotClient()


def test_function():
    # your test execution goes here
    return True


run_passed = test_function()

client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00002", "part_number": "SI001"},
    run_passed=run_passed,
    sub_units=[{"serial_number": "00102"}],
)
