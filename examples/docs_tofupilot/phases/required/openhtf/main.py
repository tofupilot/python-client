import openhtf as htf
from tofupilot.openhtf import TofuPilot


def phase_one(test):  # Phase name is the function name
    return htf.PhaseResult.CONTINUE  # Pass status


def main():
    test = htf.Test(phase_one, procedure_id="FVT1", part_number="PCB1")

    with TofuPilot(test):
        # duration and start time are automatically set
        test.execute(lambda: "PCB1A001")


if __name__ == "__main__":
    main()
