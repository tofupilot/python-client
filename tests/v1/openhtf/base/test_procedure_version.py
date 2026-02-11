"""Adapted from https://github.com/tofupilot/examples/blob/aad0dc20dd10b55a24378e9b6754712d3401d386/testing_examples/openhtf/procedure_version"""

import random

import openhtf as htf
from tofupilot.openhtf import TofuPilot


@htf.measures(htf.Measurement("button_status").equals(True))
def check_button(test):
    test.measurements.button_status = True


def test_procedure_version(tofupilot_server_url, api_key, procedure_identifier, procedure_id, extract_id_and_check_run_exists):
    test = htf.Test(
        check_button,
        procedure_id=procedure_identifier,
        procedure_version="1.2.20",
        part_number="00220",
        revision="B",
    )

    # Generate random Serial Number
    serial_number = f"00220B4K{random.randint(10000, 99999)}"

    # Execute the test
    with TofuPilot(test, url=tofupilot_server_url, api_key=api_key, stream=False):
        test.execute(lambda: serial_number)

    extract_id_and_check_run_exists(
        serial_number=serial_number,
        procedure_id=procedure_id,
        procedure_version="1.2.20",
        part_number="00220",
        revision="B",
    )
