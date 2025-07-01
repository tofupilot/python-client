import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


# Phase without measurement
def phase_connect():
    htf.PhaseResult.CONTINUE


# Phase with one measure
@htf.measures(htf.Measurement("firmware_version").equals("v2.5.1"))
def phase_firmware_version_check(test):
    test.measurements.firmware_version = "v2.5.1"


# Phase with multiple measurements
@htf.measures(
    htf.Measurement("input_voltage").in_range(
        3.1, 3.5).with_units(
            units.VOLT), htf.Measurement("output_voltage").in_range(
                1.1, 1.3).with_units(
                    units.VOLT), )
def phase_voltage_measurements(test):
    test.measurements.input_voltage = 3.3
    test.measurements.output_voltage = 1.2


def main():
    test = htf.Test(
        phase_connect,
        phase_firmware_version_check,
        phase_voltage_measurements,
        procedure_id="FVT1",  # First create procedure in Application
        part_number="PCB1",
    )

    with TofuPilot(test):
        test.execute(lambda: "PCB1A002")


if __name__ == "__main__":
    main()
