from datetime import datetime, timedelta

from tofupilot import TofuPilotClient


def step_one():
    step = [
        {
            "name": "step_one",
            "step_passed": True,
            "started_at": datetime.now(),
            "duration": timedelta(seconds=30),
            # Add a measurement with value, units and limits
            "measurement_unit": "V",
            "measurement_value": 3.3,
            "limit_low": 3.1,
            "limit_high": 3.5,
        }
    ]
    return step


def main():
    steps = step_one()

    client = TofuPilotClient()

    client.create_run(
        procedure_id="FVT1",
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCB1"},
        steps=steps,
        run_passed=all(step["step_passed"] for step in steps),
    )


if __name__ == "__main__":
    main()
