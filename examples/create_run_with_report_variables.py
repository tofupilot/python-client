from tofupilot import TofuPilotClient

client = TofuPilotClient()


def test_function():
    # your test execution goes here
    run_passed = True
    report_variables = {
        "temperature_sensor": "75°C",
        "calibration_date": "2024-06-20",
        "technician_name": "John Doe",
        "initial_temperature_reading": "72°C",
        "final_temperature_reading": "75°C",
    }
    return run_passed, report_variables


run_passed, report_variables = test_function()

response = client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "0001", "part_number": "PCB01"},
    run_passed=run_passed,
    report_variables=report_variables,
)

success = response.get("success")

assert success
