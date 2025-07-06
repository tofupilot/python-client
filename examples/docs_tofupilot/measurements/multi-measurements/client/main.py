import random
from datetime import datetime

from tofupilot import MeasurementOutcome, PhaseOutcome, TofuPilotClient

client = TofuPilotClient()


def phase_multi_measurements():
    start_time_millis = datetime.now().timestamp() * 1000

    is_connected = True
    firmware_version = "1.2.7"
    input_voltage = round(random.uniform(3.29, 3.42), 2)
    input_current = round(random.uniform(1.0, 1.55), 3)

    phase = [
        {
            "name": "phase_multi_measurements",
            "outcome": PhaseOutcome.PASS,
            "start_time_millis": start_time_millis,
            "end_time_millis": start_time_millis + 5000,
            "measurements": [
                {
                    "name": "is_connected",
                    "measured_value": is_connected,
                    "outcome": MeasurementOutcome.PASS,
                },
                {
                    "name": "firmware_version",
                    "measured_value": firmware_version,
                    "outcome": MeasurementOutcome.PASS,
                },
                {
                    "name": "input_voltage",
                    "units": "V",
                    "lower_limit": 3.2,
                    "upper_limit": 3.4,
                    "measured_value": input_voltage,
                    "outcome": (
                        MeasurementOutcome.PASS
                        if 3.2 <= input_voltage <= 3.4
                        else MeasurementOutcome.FAIL
                    ),
                },
                {
                    "name": "input_current",
                    "units": "A",
                    "upper_limit": 1.5,
                    "measured_value": input_current,
                    "outcome": (
                        MeasurementOutcome.PASS
                        if input_current <= 1.5
                        else MeasurementOutcome.FAIL
                    ),
                },
            ],
        }
    ]

    return phase


def main():
    phases = phase_multi_measurements()

    client.create_run(
        procedure_id="FVT1",
        unit_under_test={
            "serial_number": "PCB1A004",
            "part_number": "PCB01",
        },
        phases=phases,
        run_passed=all(p["outcome"] == PhaseOutcome.PASS for p in phases),
    )


if __name__ == "__main__":
    main()
