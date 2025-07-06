import random

import openhtf as htf
from openhtf.output.callbacks import json_factory
from tofupilot.openhtf import TofuPilot


@htf.measures(htf.Measurement("button_status").equals(True))
def phase_info_logger(test):
    test.measurements.button_status = True
    test.logger.info("Logging an info in the logger")


def phase_error_logger(test):
    test.logger.error("Logging error in the logger")
    return htf.PhaseResult.CONTINUE


def phase_warning_logger(test):
    test.logger.warning("Logging a warning in the logger")
    return htf.PhaseResult.CONTINUE


def phase_critical_logger(test):
    test.logger.critical("Logging a critical in the logger")
    return htf.PhaseResult.CONTINUE


def main():
    # Define the test plan with all steps
    test = htf.Test(
        phase_info_logger,
        phase_error_logger,
        phase_warning_logger,
        phase_critical_logger,
        procedure_id="FVT9",
        part_number="00220D",
    )

    # Generate random Serial Number
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"

    test.add_output_callbacks(
        json_factory.OutputToJSON(
            "test_result.json", indent=2))

    # Execute the test
    with TofuPilot(test):
        test.execute(lambda: serial_number)


if __name__ == "__main__":
    main()
