import random
from datetime import datetime, timedelta
from random import randint

from tofupilot import TofuPilotClient

# Reference time to calculate start_time_millis in milliseconds since epoch
epoch = datetime(1970, 1, 1)


# Function to calculate milliseconds since epoch
def to_millis(dt):
    return int((dt - epoch).total_seconds() * 1000)


client = TofuPilotClient()

client.create_run(
    procedure_id="FVT1",
    unit_under_test={
        "serial_number": "SN17",
        "part_number": "PNrstsrtsr",
        "batch_number": "B",
    },
    run_passed=True,  # Overall run status
    phases=[
        {
            "name": "phase_connect",  # First phase
            "outcome": "PASS",
            "start_time_millis": to_millis(
                datetime.now()
            ),  # Start time of the step in ms
            "end_time_millis": to_millis(
                datetime.now() + timedelta(seconds=5, milliseconds=12)
            ),  # End time in ms
            "measurements": [
                {
                    "name": "numeric_measurement",
                    "outcome": "PASS",
                    "measured_value": 12,
                    "units": "Hertz",
                    "lower_limit": 1,
                    "upper_limit": 20,
                },
                {
                    "name": "string_measurement",
                    "outcome": "PASS",
                    "measured_value": "Test value",
                    "units": "Unitless",
                    "docstring": "This is a string measurement example",
                },
                {
                    "name": "boolean_measurement_true",
                    "outcome": "PASS",
                    "measured_value": True,
                    "units": "BooleanUnit",
                    "docstring": "This is a boolean measurement example",
                },
                {
                    "name": "boolean_measurement_false",
                    "outcome": "PASS",
                    "measured_value": False,
                    "units": "BooleanUnit",
                    "docstring": "This is a boolean measurement example",
                },
                {
                    "name": "json_measurement",
                    "outcome": "PASS",
                    "measured_value": {"key1": "value1", "key2": 42},
                    "units": "JSONUnit",
                    "docstring": "This is a JSON measurement example",
                },
                {
                    "name": "empty_measurement",
                    "outcome": "PASS",
                    "measured_value": None,
                    "units": "EmptyUnit",
                    "docstring": "This is a measurement with a null value",
                },
                {
                    "name": "no_value_measurement",
                    "outcome": "PASS",
                    "units": "NoValueUnit",
                    "docstring": "This is a measurement with no value specified",
                },
            ],
        }
    ],
)
