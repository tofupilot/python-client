import openhtf as htf
from tofupilot.openhtf import TofuPilot


@htf.measures(htf.Measurement("is_led_switch_on").equals(True))
def phase_led(test):
    test.measurements.is_led_switch_on = True


def main():
    test = htf.Test(
        phase_led,
        procedure_id="FVT1",  # Create the procedure first in the Application
        part_number="PCB1",
    )

    with TofuPilot(test):
        test.execute(lambda: "PCB001")


if __name__ == "__main__":
    main()
