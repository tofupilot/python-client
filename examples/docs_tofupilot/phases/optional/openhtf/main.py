import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


# Decorator to set measurement name, unit and limits
@htf.measures(htf.Measurement("voltage").in_range(3.1,
              3.5).with_units(units.VOLT))
# Phase returns a Pass status because measurement (3.3) is within defined
# limits [3.1, 3.5]
def phase_voltage_measure(test):
    test.measurements.voltage = 3.3


def main():
    test = htf.Test(
        phase_voltage_measure,
        procedure_id="FVT1",
        part_number="PCB1")

    with TofuPilot(test):
        test.execute(lambda: "PCB1A001")


if __name__ == "__main__":
    main()
