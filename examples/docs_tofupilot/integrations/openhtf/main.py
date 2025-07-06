import openhtf as htf
from tofupilot.openhtf import TofuPilot  # Import OpenHTF for TofuPilot


def phase_one():
    return htf.PhaseResult.CONTINUE


def main():
    test = htf.Test(
        phase_one, procedure_id="FVT1", part_number="PCB01"
    )  # Specify procedure and part_number

    with TofuPilot(test):  # One-line integration
        test.execute(lambda: "PCB1A001")


if __name__ == "__main__":
    main()
