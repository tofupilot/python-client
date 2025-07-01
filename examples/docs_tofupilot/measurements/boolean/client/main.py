import random
from datetime import datetime

from tofupilot import MeasurementOutcome, PhaseOutcome, TofuPilotClient

client = TofuPilotClient()


def phase_led():
    start_time_millis = datetime.now().timestamp() * 1000

    phase = [
        {
            "name": "phase_led",
            "outcome": PhaseOutcome.PASS,
            "start_time_millis": start_time_millis,
            "end_time_millis": start_time_millis + 1000,
            "measurements": [
                {
                    "name": "is_led_switch_on",
                    "measured_value": True,
                    "outcome": MeasurementOutcome.PASS,
                }
            ],
        }
    ]

    return phase


def main():
    phases = phase_led()

    client.create_run(
        procedure_id="FVT1",  # Create the procedure first in the Application
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCB1"},
        phases=phases,
        run_passed=all(
            phase["outcome"] == PhaseOutcome.PASS for phase in phases),
    )


if __name__ == "__main__":
    main()
