from openhtf import Test
from tofupilot.openhtf import TofuPilot


def main():
    phases = []  # Your test phases here
    test = Test(
        phases,
        procedure_id="FVT1",  # Create the procedure first in the Application
        part_number="PCB1",
        revision="A",  # optional
        batch_number="12-24",  # optional
    )
    with TofuPilot(test):
        test.execute(lambda: "PCB1A002")  # UUT S/N


if __name__ == "__main__":
    main()
