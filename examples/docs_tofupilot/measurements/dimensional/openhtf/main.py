import random

import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


@htf.measures(
    htf.Measurement("current_voltage_resistance_over_time")
    .with_dimensions(
        units.SECOND, units.VOLT, units.AMPERE
    )  # Input axes: time, voltage, current
    .with_units(units.OHM)  # Output unit: resistance in ohms
)
def power_phase(test):
    for t in range(100):
        timestamp = t / 100
        voltage = round(random.uniform(3.3, 3.5), 2)
        current = round(random.uniform(0.3, 0.8), 3)
        resistance = voltage / current
        test.measurements.current_voltage_resistance_over_time[
            timestamp, voltage, current
        ] = resistance


def main():
    test = htf.Test(
        power_phase,
        procedure_id="FVT1",
        part_number="PCB01",
    )

    with TofuPilot(test):
        test.execute(lambda: "PCB1A003")


if __name__ == "__main__":
    main()
