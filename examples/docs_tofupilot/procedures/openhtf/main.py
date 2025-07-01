import openhtf as htf
from tofupilot.openhtf import TofuPilot


def main():
    test = htf.Test(
        procedure_id="FVT1",  # Create the procedure first in the Application
        part_number="PCB1",
    )
    with TofuPilot(test):
        # Duration calculated during execution
        test.execute(lambda: "PCB1A001")


if __name__ == "__main__":
    main()
