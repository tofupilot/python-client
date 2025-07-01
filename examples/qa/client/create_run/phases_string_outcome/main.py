import random
import time

from tofupilot import TofuPilotClient

client = TofuPilotClient()


def flash_firmware():
    passed = bool(random.randint(0, 1))
    measured_value = "1.2.4" if passed else "1.2.0"
    return passed, measured_value, None, None, None


def handle_test():
    serial_number = f"SI0364A{random.randint(10000, 99999)}"

    start_time = int(time.time() * 1000)
    passed, measured_value, unit, limit_low, limit_high = flash_firmware()
    end_time = int(time.time() * 1000)

    outcome = "PASS" if passed else "FAIL"

    phase = {
        "name": "flash_firmware",
        "outcome": outcome,
        "start_time_millis": start_time,
        "end_time_millis": end_time,
        "measurements": [
            {
                "name": "flash_firmware",
                "outcome": outcome,
                "measured_value": measured_value,
                "units": unit,
                "lower_limit": limit_low,
                "upper_limit": limit_high,
            }
        ],
    }

    client.create_run(
        procedure_id="FVT9",
        procedure_name="Test_QA",
        unit_under_test={
            "part_number": "SI03645A",
            "part_name": "test-QA",
            "revision": "3.1",
            "batch_number": "11-24",
            "serial_number": serial_number,
        },
        run_passed=passed,
        phases=[phase],
    )


if __name__ == "__main__":
    handle_test()
