import openhtf as htf
from tofupilot.openhtf import TofuPilot


def phase_file_attachment(test):
    test.attach_from_file("data/sample_file.txt")
    return htf.PhaseResult.CONTINUE


def main():
    test = htf.Test(
        phase_file_attachment,
        procedure_id="TEST0",
        part_number="00389")
    with TofuPilot(test):
        test.execute(lambda: "PCB0001")


if __name__ == "__main__":
    main()
