import random

import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


@htf.measures(
    htf.Measurement("is_connected").equals(True),  # Boolean measure
    htf.Measurement("firmware_version").equals("1.2.7"),  # String measure
    htf.Measurement("input_voltage").in_range(3.2, 3.4).with_units(units.VOLT),
    htf.Measurement("input_current").in_range(
        maximum=1.5).with_units(units.AMPERE),
)
def phase_multi_measurements(test):
    test.measurements.is_connected = True
    test.measurements.firmware_version = "1.2.7"

    test.measurements.input_voltage = round(random.uniform(3.29, 3.42), 2)
    test.measurements.input_current = round(random.uniform(1.0, 1.55), 3)


def main():
    test = htf.Test(
        phase_multi_measurements,
        procedure_id="FVT1",
        part_number="PCB01",
    )

    with TofuPilot(test):
        test.execute(lambda: "PCB1A004")


if __name__ == "__main__":
    main()
