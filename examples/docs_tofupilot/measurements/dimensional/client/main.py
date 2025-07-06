import random
from datetime import datetime

import numpy as np
from tofupilot import MeasurementOutcome, PhaseOutcome, TofuPilotClient

client = TofuPilotClient()


def standard():
    """Python lists approach - one point at a time"""
    start = datetime.now().timestamp() * 1000
    measurements = []

    for t in range(100):
        timestamp = t / 100  # Time dimension
        voltage = round(random.uniform(3.3, 3.5), 2)  # Voltage dimension
        current = round(random.uniform(0.3, 0.8), 3)  # Current dimension
        measurements.append((timestamp, voltage, current, voltage / current))

    return {
        "name": "loop_approach",
        "outcome": PhaseOutcome.PASS,
        "start_time_millis": start,
        "end_time_millis": start + 30000,
        "measurements": [
            {
                "name": "current_voltage_resistance_over_time",
                "units": ["s", "V", "A", "Ohm"],
                "measured_value": measurements,
                "outcome": MeasurementOutcome.PASS,
            }
        ],
    }


def numpy_way():
    """NumPy approach - all points at once"""
    start = datetime.now().timestamp() * 1000

    # Generate all dimensions simultaneously
    timestamps = np.linspace(0, 0.99, 100)
    voltages = np.round(np.random.uniform(3.3, 3.5, 100), 2)
    currents = np.round(np.random.uniform(0.3, 0.8, 100), 3)

    measurements = [
        tuple(x)
        for x in np.column_stack((timestamps, voltages, currents, voltages / currents))
    ]

    return {
        "name": "vector_approach",
        "outcome": PhaseOutcome.PASS,
        "start_time_millis": start,
        "end_time_millis": start + 30000,
        "measurements": [
            {
                "name": "current_voltage_resistance_over_time",
                "units": ["s", "V", "A", "Ohm"],
                "measured_value": measurements,
                "outcome": MeasurementOutcome.PASS,
            }
        ],
    }


def main():
    client.create_run(
        procedure_id="FVT1",
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCB1"},
        phases=[standard(), numpy_way()],
        run_passed=True,
    )


if __name__ == "__main__":
    main()
