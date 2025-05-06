from openhtf import Test, PhaseResult
from openhtf.plugs import user_input
import time
import sys


import openhtf as htf
from openhtf.plugs.user_input import UserInput
from tofupilot.openhtf import TofuPilot


def power_on(test):
    time.sleep(0.1)
    return PhaseResult.CONTINUE


def log_1(test):
    time.sleep(0.1)
    return PhaseResult.CONTINUE


def log_2(test):
    time.sleep(0.1)
    return PhaseResult.CONTINUE


def log_3(test):
    time.sleep(0.1)
    return PhaseResult.CONTINUE


def log_4(test):
    time.sleep(0.1)
    return PhaseResult.CONTINUE


@htf.measures(
    htf.Measurement("led_color").with_validator(
        lambda color: color in ["Red", "Green", "Blue"]
    )
)
@htf.plug(user_input=UserInput)
def prompt_operator_led_color(test, user_input):
    led_color = user_input.prompt(message="What is the LED color? (Red/Green/Blue)")
    test.measurements.led_color = led_color


def main():
    test = Test(
        power_on,
        log_1,
        log_2,
        log_3,
        log_4,
        prompt_operator_led_color,
        procedure_id="FVT1",
        part_number="AAA",
    )

    try:
        # Add TofuPilot context manager
        with TofuPilot(test, url="http://localhost:3000"):
            # Execute the test with standard OpenHTF execution
            result = test.execute(
                test_start=user_input.prompt_for_test_start()
            )

            # Print the test name and outcome in the exact format requested
            test_name = test.metadata.get('test_name', 'openhtf_test')
            print("\n======================= test: {0}  outcome: {1} =======================\n".format(
                test_name, result.outcome.name))
            # Will continue with TofuPilot upload messages (already handled by the callback)
    except KeyboardInterrupt:
        # This catches Ctrl+C outside of the test execution
        print("\nTest setup interrupted. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"Error during test execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
