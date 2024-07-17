import time
from datetime import datetime

from tofupilot import TofuPilotClient

client = TofuPilotClient()


def test_function():
    # Your test execution goes here
    time.sleep(1)

    run_passed = True
    report_variables = {
        "initial_temperature_reading": "72°C",
        "final_temperature_reading": "75°C",
    }
    attachments = ["data/temperature-map.png", "data/performance-report.pdf"]

    return run_passed, report_variables, attachments


# Measure the duration of the test_function
start_time = datetime.now()
run_passed, report_variables, attachments = test_function()
end_time = datetime.now()
duration = end_time - start_time

client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
    run_passed=run_passed,
    duration=duration,
    report_variables=report_variables,
    attachments=attachments,
)
