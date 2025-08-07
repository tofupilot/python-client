"""Adapted from https://github.com/tofupilot/examples/tree/aad0dc20dd10b55a24378e9b6754712d3401d386/testing_examples/openhtf/generic"""

import random
import time
from datetime import datetime, timedelta

import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


@htf.measures(htf.Measurement("firmware_version").equals("1.4.3"))
def pcba_firmware_version(test):
    test.measurements.firmware_version = "1.4.3" if random.random() < 0.99 else "1.4.2"


@htf.measures(htf.Measurement("button_status").equals(True))
def check_button(test):
    test.measurements.button_status = random.choice([True, False])
    time.sleep(1)

@htf.measures(htf.Measurement("input_voltage").in_range(4.5,
              5).with_units(units.VOLT))
def check_voltage_input(test):
    test.measurements.input_voltage = round(random.uniform(3.7, 4.9), 2)


@htf.measures(
    htf.Measurement("output_voltage").in_range(3.2, 3.4).with_units(units.VOLT)
)
def check_voltage_output(test):
    test.measurements.output_voltage = round(random.uniform(2.95, 3.35), 2)


@htf.measures(
    htf.Measurement("current_protection_triggered")
    .in_range(maximum=1.5)
    .with_units(units.AMPERE)
)
def check_overcurrent_protection(test):
    test.measurements.current_protection_triggered = round(
        random.uniform(1.0, 1.7), 3)
    time.sleep(1)


def check_battery_switch():
    if random.random() < 0.9:
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP


@htf.measures(
    htf.Measurement("efficiency").in_range(85, 98).with_units(units.Unit("%"))
)
def check_converter_efficiency(test):
    input_power = 500
    output_power = round(random.uniform(425, 480))
    test.measurements.efficiency = round(
        ((output_power / input_power) * 100), 1)
    time.sleep(1)


def visual_control_pcb_coating(test):
    if random.random() < 0.98:
        test.attach_from_file("tests/v1/attachments/oscilloscope.jpeg")
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP


def test_generic(tofupilot_server_url, api_key, procedure_identifier, procedure_id, extract_id_and_check_run_exists):
    # Define the test plan with all steps
    test = htf.Test(
        pcba_firmware_version,
        check_button,
        check_voltage_input,
        check_voltage_output,
        check_overcurrent_protection,
        check_battery_switch,
        check_converter_efficiency,
        visual_control_pcb_coating,
        procedure_id=procedure_identifier,
        part_number="00220",
        revision="A",
        batch_number="1024-0001",
        # sub_units=[{"serial_number": "00102"}],
    )

    # Generate random Serial Number
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220B4K{random_digits}"

    # Execute the test
    with TofuPilot(test, url=tofupilot_server_url, api_key=api_key):
        test.execute(lambda: serial_number)

    
    extract_id_and_check_run_exists(serial_number=serial_number, procedure_id=procedure_id, part_number="00220", revision="A", batch_number="1024-0001")
