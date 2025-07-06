import random
from datetime import datetime

from tofupilot import MeasurementOutcome, PhaseOutcome, TofuPilotClient


def main(serial_number: str):
    client = TofuPilotClient()
    start_time_millis = datetime.now().timestamp() * 1000

    # Motor test
    motor_running = random.choice([True, False])
    motor_outcome = (
        MeasurementOutcome.PASS if motor_running else MeasurementOutcome.FAIL
    )
    motor_phase = {
        "name": "check_motor",
        "outcome": motor_outcome,
        "start_time_millis": start_time_millis,
        "end_time_millis": start_time_millis + 3000,  # example duration
        "measurements": [
            {
                "name": "motor_running",
                "measured_value": motor_running,
                "outcome": motor_outcome,
            }
        ],
    }

    # Battery test
    battery_voltage = round(random.uniform(11.0, 12.6), 2)
    battery_current = round(random.uniform(1.0, 2.5), 2)
    battery_voltage_outcome = (
        MeasurementOutcome.PASS
        if 11.0 <= battery_voltage <= 12.6
        else MeasurementOutcome.FAIL
    )
    battery_current_outcome = (
        MeasurementOutcome.PASS
        if 1.0 <= battery_current <= 2.5
        else MeasurementOutcome.FAIL
    )
    battery_phase = {
        "name": "check_battery",
        "outcome": (
            PhaseOutcome.PASS
            if battery_voltage_outcome == MeasurementOutcome.PASS
            and battery_current_outcome == MeasurementOutcome.PASS
            else PhaseOutcome.FAIL
        ),
        "start_time_millis": start_time_millis,
        "end_time_millis": start_time_millis + 3000,  # example duration
        "measurements": [
            {
                "name": "battery_voltage",
                "measured_value": battery_voltage,
                "units": "V",
                "outcome": battery_voltage_outcome,
                "lower_limit": 11.0,
                "upper_limit": 12.6,
            },
            {
                "name": "battery_current",
                "measured_value": battery_current,
                "units": "A",
                "outcome": battery_current_outcome,
                "lower_limit": 1.0,
                "upper_limit": 2.5,
            },
        ],
    }

    # Create run
    phases = [motor_phase, battery_phase]
    client.create_run(
        procedure_id="VANILLA",
        unit_under_test={
            "serial_number": serial_number,
            "part_number": "FP01",
        },
        phases=phases,
        run_passed=all(
            phase["outcome"] == PhaseOutcome.PASS for phase in phases),
    )


if __name__ == "__main__":
    main(f"FP01{random.randint(100, 999)}")
