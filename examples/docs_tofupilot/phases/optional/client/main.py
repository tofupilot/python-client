from datetime import datetime, timedelta

from tofupilot import MeasurementOutcome, PhaseOutcome, TofuPilotClient

client = TofuPilotClient()


# Phase returns a Pass status because measurement (3.3) is within defined
# limits [3.1, 3.5]
def phase_voltage_measure():
    start_time_millis = datetime.now().timestamp() * 1000

    phase = {
        "name": "voltage_measure_phase",
        "outcome": PhaseOutcome.PASS,
        "start_time_millis": start_time_millis,
        "end_time_millis": start_time_millis
        + 30 * 1000,  # Indicating phase took 30 seconds to complete
        "measurements": [
            {
                "name": "voltage",
                "units": "V",
                "lower_limit": 3.1,
                "upper_limit": 3.5,
                "measured_value": 3.3,
                "outcome": MeasurementOutcome.PASS,
            }
        ],
    }

    return phase


def main():
    phases = [phase_voltage_measure()]

    client.create_run(
        procedure_id="FVT1",  # Create the procedure first in the Application
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCB1"},
        phases=phases,
        run_passed=all(
            phase["outcome"] == PhaseOutcome.PASS for phase in phases),
    )


if __name__ == "__main__":
    main()
