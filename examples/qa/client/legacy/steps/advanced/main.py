from datetime import datetime, timedelta

from tofupilot import TofuPilotClient


def main():
    client = TofuPilotClient()

    client.create_run(
        procedure_id="FVT1",
        unit_under_test={
            "serial_number": "PCB1A002",
            "part_number": "PCB1",
        },
        run_passed=True,
        steps=[
            {
                "name": "step_connect",
                "step_passed": True,
                "duration": timedelta(seconds=3),
                "started_at": datetime.now(),
            },
            {
                "name": "test_firmware_version_check",
                "step_passed": True,
                "duration": timedelta(minutes=1, seconds=42),
                "started_at": datetime.now() + timedelta(seconds=3),
                "measurement_value": "v2.5.1",
            },
            {
                "name": "step_temp_calibration",
                "step_passed": True,
                "duration": timedelta(milliseconds=500),
                "started_at": datetime.now() + timedelta(seconds=4),
                "measurement_value": 75,
                "measurement_unit": "°C",
                "limit_low": 70,
                "limit_high": 80,
            },
        ],
    )


if __name__ == "__main__":
    main()
