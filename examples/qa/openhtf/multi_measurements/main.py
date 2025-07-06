import random

import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


@htf.measures(
    htf.Measurement("firmware_version").equals("1.4.3"),
    htf.Measurement("power_mode_functional").equals("on"),
)
def string_test(test):
    test.measurements.firmware_version = "1.4.3" if random.random() < 0.99 else "1.4.2"
    test.measurements.power_mode_functional = "on"


@htf.measures(htf.Measurement("button_status").equals(True))
def boolean_test(test):
    test.measurements.button_status = True


def phaseresult_test():
    return htf.PhaseResult.CONTINUE


@htf.measures(
    htf.Measurement("two_limits").in_range(
        4.5, 5).with_units(
            units.VOLT), htf.Measurement("one_limit").in_range(
                maximum=1.5).with_units(
                    units.AMPERE), htf.Measurement("percentage").in_range(
                        85, 98).with_units(
                            units.Unit("%")), )
def measure_test_with_limits(test):
    test.measurements.two_limits = round(random.uniform(3.8, 4.9), 2)
    test.measurements.one_limit = round(random.uniform(1.0, 1.6), 3)
    input_power = 500
    output_power = round(random.uniform(425, 480))
    test.measurements.percentage = round(
        ((output_power / input_power) * 100), 1)


@htf.measures(htf.Measurement("is_connected").equals(True),
              htf.Measurement("firmware_version").equals("1.2.7"),
              htf.Measurement("temperature").in_range(20,
                                                      25).with_units(units.DEGREE_CELSIUS),
              )
def phase_multi_measurements(test):
    test.measurements.is_connected = True
    test.measurements.firmware_version = (
        "1.2.7" if test.measurements.is_connected else "N/A"
    )
    test.measurements.temperature = round(random.uniform(22.5, 23), 2)


@htf.measures(
    htf.Measurement("dimensions").with_dimensions(units.HERTZ),
    htf.Measurement("lots_of_dims").with_dimensions(
        units.HERTZ,
        units.SECOND,
        htf.Dimension(description="my_angle", unit=units.RADIAN),
    ),
)
def dimensions(test):
    """Phase with dimensioned measurements."""
    for dim in range(5):
        test.measurements.dimensions[dim] = 1 << dim
    for x, y, z in zip(
        list(
            range(
            1, 5)), list(
                range(
                    21, 25)), list(
                        range(
                            101, 105))):
        test.measurements.lots_of_dims[x, y, z] = x + y + z


@htf.measures(
    htf.Measurement("binary_measure").equals(True),
    htf.Measurement("string_measure").equals("1.2.7"),
    htf.Measurement("numerical_measure")
    .in_range(20, 25)
    .with_units(units.DEGREE_CELSIUS),
)
def not_working_multi_measurements(test):
    test.measurements.binary_measure = 42
    test.measurements.string_measure = 123
    test.measurements.numerical_measure = 35


def main():
    # Define the test plan with all steps
    test = htf.Test(
        phase_multi_measurements,
        dimensions,
        string_test,
        boolean_test,
        phaseresult_test,
        measure_test_with_limits,
        not_working_multi_measurements,
        procedure_id="FVT9",
        part_number="00220D",
    )

    # Generate random Serial Number
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"

    # Execute the test
    with TofuPilot(test):
        test.execute(lambda: serial_number)


if __name__ == "__main__":
    main()
