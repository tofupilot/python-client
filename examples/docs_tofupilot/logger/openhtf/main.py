import openhtf as htf
from tofupilot.openhtf import TofuPilot


@htf.measures(htf.Measurement("boolean_measure").equals(True))
def phase_with_info_logger(test):
    test.measurements.boolean_measure = True
    # You can log info, warning, error, and critical. By default, debug.
    test.logger.info("Logging an information")


def main():
    test = htf.Test(
        phase_with_info_logger,
        procedure_id="FVT1",
        part_number="PCB01",
    )

    with TofuPilot(test):
        test.execute(lambda: "PCB1A001")


if __name__ == "__main__":
    main()
