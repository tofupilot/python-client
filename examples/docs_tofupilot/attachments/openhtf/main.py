import openhtf as htf
from tofupilot.openhtf import TofuPilot


def phase_file_attachment(test):
    # Replace with your file path
    test.attach_from_file("data/temperature-map.png")
    return htf.PhaseResult.CONTINUE


def main():
    test = htf.Test(
        phase_file_attachment,
        procedure_id="FVT1",  # Create the procedure first in the Application
        part_number="PCB1",
    )

    with TofuPilot(test):
        test.execute(lambda: "PCB1A001")


if __name__ == "__main__":
    main()
