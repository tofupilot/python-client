"""
Example script demonstrating how to create a test run in TofuPilot with detailed steps.

This script runs a series of test functions, records the results and duration of each step, 
and then creates a test run in TofuPilot. Each step includes detailed information such as 
the measured value, unit, and thresholds.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""

from tofupilot import TofuPilotClient
from datetime import datetime

# Initialize the TofuPilot client
client = TofuPilotClient()


def initial_temperature_check():
    """
    Simulates an initial temperature check.
    """
    return True, 72.0, "°C", None, None


def temperature_calibration():
    """
    Simulates a temperature calibration check.
    """
    return True, 75.0, "°C", 70.0, 80.0


def final_temperature_check():
    """
    Simulates a final temperature check.
    """
    return True, 75.0, "°C", None, None


def run_all_tests():
    """
    Runs all defined tests and records the results of each step.
    """
    tests = [
        initial_temperature_check,
        temperature_calibration,
        final_temperature_check,
    ]
    steps = []
    all_tests_passed = True

    for test in tests:
        start_time = datetime.now()
        passed, value_measured, unit, min_threshold, max_threshold = test()
        end_time = datetime.now()

        step = {
            "name": test.__name__,
            "step_passed": passed,
            "started_at": start_time,
            "duration": end_time - start_time,
            "measurement_unit": unit,
            "measurement_value": value_measured,
            "limit_low": min_threshold,
            "limit_high": max_threshold,
        }

        steps.append(step)

        if not passed:
            all_tests_passed = False

    return all_tests_passed, steps


# Run the tests and create the run in TofuPilot
run_passed, steps = run_all_tests()

response = client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "0001"},
    run_passed=run_passed,
    steps=steps,
)

# Ensure the run was successfully created
success = response.get("success")

assert success
