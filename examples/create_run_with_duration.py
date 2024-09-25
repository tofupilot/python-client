import time
from datetime import timedelta

from tofupilot import TofuPilotClient

client = TofuPilotClient()


def test_function():
    # Your test execution goes here
    time.sleep(1)  # Placeholder for test execution time
    return True


# Measure the duration of the test_function (optional)
start_time = time.time()
run_passed = test_function()
end_time = time.time()
duration = end_time - start_time

response = client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
    run_passed=run_passed,
    duration=timedelta(seconds=end_time - start_time),  # Optional argument
)

success = response.get("success")

assert success
