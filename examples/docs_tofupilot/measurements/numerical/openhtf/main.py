import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


@htf.measures(
    htf.Measurement("temperature")  # Declares the measurement name
    .in_range(0, 100)  # Defines the lower and upper limits
    .with_units(units.DEGREE_CELSIUS)  # Specifies the unit
)
def phase_temperature(test):
    test.measurements.temperature = 25  # Set the temperature measured value to 25°C


def main():
    test = htf.Test(
        phase_temperature,
        procedure_id="FVT1",  # Create the procedure first in the Application
        part_number="PCB1",
    )

    with TofuPilot(test):
        test.execute(lambda: "PCB001")


if __name__ == "__main__":
    main()
