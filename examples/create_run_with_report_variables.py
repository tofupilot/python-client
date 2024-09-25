from tofupilot import TofuPilotClient

client = TofuPilotClient()


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

success = response.get("success")

assert success
