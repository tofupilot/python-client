from openhtf import PhaseResult, Test
from tofupilot.openhtf import TofuPilot

# Please ensure both units PCB1A001 and LEN1A001 exist before running this script
# Refer to https://tofupilot.com/docs/procedures for an example on how to
# create them


def main():
    test = Test(
        procedure_id="FVT2",  # Create the procedure first in the Application
        part_number="CAM1",
        sub_units=[{"serial_number": "PCB1A001"},
                   {"serial_number": "LEN1A001"}],
    )
    with TofuPilot(test):
        test.execute(lambda: "CAM1A001")


if __name__ == "__main__":
    main()
