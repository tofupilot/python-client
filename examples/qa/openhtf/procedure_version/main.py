import random

import openhtf as htf
from tofupilot.openhtf import TofuPilot


@htf.measures(htf.Measurement("button_status").equals(True))
def check_button(test):
    test.measurements.button_status = bool(random.randint(0, 1))


def main():
    test = htf.Test(
        check_button,
        procedure_id="FVT1",  # No need to specify the ID
        procedure_version="1.2.20",  # Create procedure version
        part_number="00220",
        revision="B",
    )

    # Generate random Serial Number
    serial_number = f"00220B4K{random.randint(10000, 99999)}"

    # Execute the test
    with TofuPilot(test, stream=False):
        test.execute(lambda: serial_number)


if __name__ == "__main__":
    main()
