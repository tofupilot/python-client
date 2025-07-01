from datetime import datetime, timedelta

from tofupilot import MeasurementOutcome, PhaseOutcome, TofuPilotClient

client = TofuPilotClient()


def main():
    start_time_millis = datetime.now().timestamp() * 1000

    client.create_run(
        procedure_id="FVT1",  # Create the procedure first in the Application
        unit_under_test={
            "serial_number": "PCB1A002",
            "part_number": "PCB1",
        },
        run_passed=True,
        phases=[
            # Phase without measurement
            {
                "name": "phase_connect",
                "outcome": PhaseOutcome.PASS,
                "start_time_millis": start_time_millis,
                "end_time_millis": start_time_millis
                + 3000,  # phase duration of 3 seconds
            },
            # Phase with measurement
            {
                "name": "phase_firmware_version_check",
                "outcome": PhaseOutcome.PASS,
                "start_time_millis": start_time_millis + 3000,
                "end_time_millis": start_time_millis
                + 6000,  # phase duration of 3 seconds
                "measurements": [
                    {
                        "name": "firmware_version",
                        "outcome": MeasurementOutcome.PASS,
                        "measured_value": "v2.5.1",
                    }
                ],
            },
            # Phase with multiple measurements
            {
                "name": "phase_voltage_measurements",
                "outcome": PhaseOutcome.PASS,
                "start_time_millis": start_time_millis + 9000,
                "end_time_millis": start_time_millis
                + 19000,  # phase duration of 10 seconds
                "measurements": [
                    {
                        "name": "input_voltage",
                        "outcome": MeasurementOutcome.PASS,
                        "measured_value": 3.3,
                        "units": "V",
                        "lower_limit": 3.1,
                        "upper_limit": 3.5,
                    },
                    {
                        "name": "output_voltage",
                        "outcome": MeasurementOutcome.PASS,
                        "measured_value": 1.2,
                        "units": "V",
                        "lower_limit": 1.1,
                        "upper_limit": 1.3,
                    },
                ],
            },
        ],
    )


if __name__ == "__main__":
    main()
