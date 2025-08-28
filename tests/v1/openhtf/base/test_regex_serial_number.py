"""Adapted from https://github.com/tofupilot/examples/tree/aad0dc20dd10b55a24378e9b6754712d3401d386/testing_examples/openhtf/regex_serial_number"""

import random

import openhtf as htf
from tofupilot.openhtf import TofuPilot


@htf.measures(htf.Measurement("button_status").equals(True))
def check_button(test):
    test.measurements.button_status = False

def test_procedure_verion(tofupilot_server_url, api_key, procedure_identifier, procedure_id, extract_id_and_check_run_exists):
    test = htf.Test(
        check_button,
        procedure_id=procedure_identifier,
    )

    with TofuPilot(test, url=tofupilot_server_url, api_key=api_key):
        test.execute(lambda: "PCB101T5A123")

    extract_id_and_check_run_exists( # Set to "First 8 characters" `^([A-Z0-9]{8})`
        serial_number="PCB101T5A123",
        procedure_id=procedure_id,
        part_number="PCB101T5",
        outcome="FAIL"
    )