import openhtf as htf
from tofupilot.openhtf import TofuPilot


@htf.measures(htf.Measurement("firmware_version").equals("1.2.4"))
def phase_firmware(test):
    test.measurements.firmware_version = "1.2.4"


def main():
    test = htf.Test(
        phase_firmware,
        procedure_id="FVT1",  # Create the procedure first in the Application
        part_number="PCB1",
    )

    with TofuPilot(test):
        test.execute(lambda: "PCB001")


if __name__ == "__main__":
    main()
