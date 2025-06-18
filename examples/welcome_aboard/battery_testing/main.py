import random
from datetime import datetime, timedelta

from tofupilot import TofuPilotClient

client = TofuPilotClient()


# Simulate passing probability for a test result
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


# Cell Test Functions
def esr_test():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(
            random.uniform(
                5,
                10),
            2) if passed else round(
            random.uniform(
                15,
                20),
            2))
    return passed, value_measured, "mΩ", 5, 15


def cell_voltage_test():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(3.0, 3.5), 2)
        if passed
        else round(random.uniform(2.5, 2.9), 2)
    )
    return passed, value_measured, "V", 3.0, 3.5


def ir_test():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(
            random.uniform(
                5,
                10),
            2) if passed else round(
            random.uniform(
                15,
                20),
            2))
    return passed, value_measured, "mΩ", 5, 15


def charge_discharge_cycle_test():
    passed = simulate_test_result(0.95)
    value_measured = (
        round(random.uniform(95, 100), 1)
        if passed
        else round(random.uniform(80, 94), 1)
    )
    return passed, value_measured, "% Capacity", 95, 100


# PCBA Test function
def flash_firmware_and_version():
    passed = simulate_test_result(0.99)
    value_measured = "1.2.8" if passed else None
    return passed, value_measured, None, None, None


def configuration_battery_gauge():
    passed = simulate_test_result(0.98)
    return passed, None, None, None, None


def get_calibration_values_and_internal_statuses():
    passed = simulate_test_result(0.98)
    return passed, None, None, None, None


def overvoltage_protection_test():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(4.20, 4.25), 3)
        if passed
        else round(random.uniform(4.30, 4.35), 3)
    )
    return passed, value_measured, "V", 4.20, 4.25


def undervoltage_protection_test():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(2.5, 2.6), 2)
        if passed
        else round(random.uniform(2.3, 2.4), 2)
    )
    return passed, value_measured, "V", 2.5, 2.6


def test_LED_and_button():
    passed = simulate_test_result(0.95)
    return passed, None, None, None, None


def save_information_in_memory():
    passed = simulate_test_result(0.99)
    return passed, None, None, None, None


def config_battery_gauge():
    passed = simulate_test_result(0.95)
    return passed, None, None, None, None


def calibrate_temperature():
    passed = simulate_test_result(0.98)
    value_measured = round(random.uniform(20.0, 25.0), 1)
    return passed, value_measured, "°C", 20, 25


# Assembly Test Functions
def battery_connection():
    passed = simulate_test_result(1.0)
    return passed, None, None, None, None


def voltage_value():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(10.0, 12.0), 2)
        if passed
        else round(random.uniform(8.0, 9.5), 2)
    )
    return passed, value_measured, "V", 10.0, 12.0


def internal_resistance():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(
            random.uniform(
                5,
                10),
            2) if passed else round(
            random.uniform(
                15,
                20),
            2))
    return passed, value_measured, "mΩ", 5, 15


def thermal_runaway_detection():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(
            random.uniform(
                55,
                65),
            2) if passed else round(
            random.uniform(
                66,
                70),
            2))
    return passed, value_measured, "°C", 55, 65


def state_of_health():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(95, 100), 1)
        if passed
        else round(random.uniform(85, 94), 1)
    )
    return passed, value_measured, "%", 95, None


def state_of_charge():
    passed = simulate_test_result(0.98)
    value_measured = (
        round(
            random.uniform(
                40,
                60),
            1) if passed else round(
            random.uniform(
                25,
                35),
            1))
    return passed, value_measured, "%", 40, 60


def visual_inspection():
    passed = simulate_test_result(1)
    return passed, None, None, None, None


# Run a single test
def run_test(test, duration):
    start_time = datetime.now()
    passed, value_measured, unit, limit_low, limit_high = test()

    step = {
        "name": test.__name__,
        "started_at": start_time,
        "duration": duration,
        "step_passed": passed,
        "measurement_unit": unit,
        "measurement_value": value_measured,
        "limit_low": limit_low,
        "limit_high": limit_high,
    }
    return passed, step


def run_all_tests(tests, previous_failed_step=None):
    steps = []
    all_tests_passed = True
    failed_at_step = None

    for index, (test, duration) in enumerate(tests):
        if previous_failed_step is not None and index == previous_failed_step["index"]:
            passed = previous_failed_step["step_passed"]
            step = previous_failed_step
        else:
            passed, step = run_test(test, duration)

        steps.append(step)

        if not passed:
            failed_at_step = {
                "index": index,
                "step_passed": passed,
                "name": step["name"],
                "started_at": step["started_at"],
                "duration": step["duration"],
                "measurement_unit": step["measurement_unit"],
                "measurement_value": step["measurement_value"],
                "limit_low": step["limit_low"],
                "limit_high": step["limit_high"],
            }
            all_tests_passed = False
            break

    return all_tests_passed, steps, failed_at_step


# Run a list of tests sequentially
def handle_procedure(
    procedure_id,
    tests,
    serial_number,
    part_number,
    revision,
    batch_number,
    sub_units,
    attachments,
):
    run_passed, steps, failed_step = run_all_tests(tests)

    if procedure_id == "FVT3" and run_passed:  # Assembly Procedure
        internal_resistance = steps[2]["measurement_value"]
        voltage_value = steps[1]["measurement_value"]

    client.create_run(
        procedure_id=procedure_id,
        unit_under_test={
            "part_number": part_number,
            "revision": revision,
            "serial_number": serial_number,
            "batch_number": batch_number,
        },
        run_passed=run_passed,
        steps=steps,
        sub_units=sub_units,
        attachments=attachments,
    )
    return run_passed, failed_step


# Main Function for Executing Procedures
def execute_procedures(end):
    for _ in range(end):
        # Generate unique serial numbers
        part_number_cell = "00143"
        part_number_pcb = "00786"
        part_number_assembly = "SI02430"
        revision_cell = "A"
        revision_pcb = "B"
        revision_assembly = "B"
        static_segment = "4J"
        random_digits_cell = "".join(
            [str(random.randint(0, 9)) for _ in range(5)])
        random_digits_pcb = "".join(
            [str(random.randint(0, 9)) for _ in range(5)])
        random_digits_assembly = "".join(
            [str(random.randint(0, 9)) for _ in range(5)])
        serial_number_cell = (
            f"{part_number_cell}{revision_cell}{static_segment}{random_digits_cell}"
        )
        serial_number_pcb = (
            f"{part_number_pcb}{revision_pcb}{static_segment}{random_digits_pcb}"
        )
        serial_number_assembly = f"{part_number_assembly}{revision_assembly}{static_segment}{random_digits_assembly}"
        batch_number = "1024"

        # Execute PCBA Tests
        tests_pcb = [
            (flash_firmware_and_version, timedelta(seconds=90)),
            (configuration_battery_gauge, timedelta(seconds=1)),
            (get_calibration_values_and_internal_statuses, timedelta(seconds=1)),
            (overvoltage_protection_test, timedelta(seconds=5)),
            (undervoltage_protection_test, timedelta(seconds=5)),
            (test_LED_and_button, timedelta(seconds=6)),
            (save_information_in_memory, timedelta(seconds=0.1)),
            (visual_inspection, timedelta(seconds=10)),
        ]
        passed_pcb, failed_step_pcb = handle_procedure(
            "FVT1",
            tests_pcb,
            serial_number_pcb,
            part_number_pcb,
            revision_pcb,
            batch_number,
            None,
            ["data/pcb_coating.jpeg"],
        )
        if not passed_pcb:
            continue

        # Execute Cell Tests
        tests_cell = [
            (esr_test, timedelta(seconds=2)),
            (cell_voltage_test, timedelta(seconds=0.1)),
            (ir_test, timedelta(seconds=5)),
            (charge_discharge_cycle_test, timedelta(seconds=2)),
        ]
        passed_cell, failed_step_cell = handle_procedure(
            "FVT2",
            tests_cell,
            serial_number_cell,
            part_number_cell,
            revision_cell,
            batch_number,
            None,
            None,
        )
        if not passed_cell:
            continue

        # Execute Assembly Tests
        tests_assembly = [
            (battery_connection, timedelta(seconds=0.1)),
            (voltage_value, timedelta(seconds=1)),
            (internal_resistance, timedelta(seconds=1)),
            (thermal_runaway_detection, timedelta(seconds=2)),
            (state_of_health, timedelta(seconds=2)),
            (state_of_charge, timedelta(seconds=2)),
        ]
        handle_procedure(
            "FVT4",
            tests_assembly,
            serial_number_assembly,
            part_number_assembly,
            revision_assembly,
            batch_number,
            [
                {"serial_number": serial_number_pcb},
                {"serial_number": serial_number_cell},
            ],
            None,
        )


if __name__ == "__main__":
    execute_procedures(1)
