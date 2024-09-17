# This script automates the testing process for multiple cables in a batch.
# It generates a unique 8-character serial number for each cable, prompts the user for the test result,
# and logs the test outcome to the TofuPilot system. Failed tests can be retried, and the user
# can decide whether to continue with the next test or end the process.

from tofupilot import TofuPilotClient
import uuid  # Make sure to install shortuuid beforehand using `pip install shortuuid`

# Replace with your own information
procedure_id = "FVT1"
batch_number = "001"
part_number = "CBL"
revision = "1.0"
steps = []  # List of test steps, adapt according to your needs

# Check https://docs.tofupilot.com/ to save your API key as an environment variable
client = TofuPilotClient()


# Function to test a cable
def test_cable():
    # Test logic, here we simulate a test
    test_result = input("Test result (OK/KO): ").strip().upper()
    return test_result == "OK"


# Loop to test multiple cables in a batch
while True:
    # Generate the serial number of the cable
    random_id = str(uuid.uuid4())[:8]  # Limit the UUID to 8 characters
    serial_number = f"{batch_number}-{random_id}"

    print(f"\nTesting cable {serial_number}")

    # Perform the test
    run_passed = test_cable()

    # Send the result to TofuPilot
    client.create_run(
        procedure_id=procedure_id,
        unit_under_test={
            "part_number": part_number,
            "revision": revision,
            "serial_number": serial_number,
        },
        run_passed=run_passed,
        steps=steps,
    )

    # If the test fails, offer to retry
    while not run_passed:
        retry = (
            input(f"Test {serial_number} failed. Do you want to retry? (y/n): ")
            .strip()
            .lower()
        )
        if retry == "y":
            # Retest with the same serial number
            run_passed = test_cable()
            client.create_run(
                procedure_id=procedure_id,
                unit_under_test={
                    "part_number": part_number,
                    "revision": revision,
                    "serial_number": serial_number,
                },
                run_passed=run_passed,
                steps=steps,
            )
        else:
            # Move on to the next test
            break

    # Ask if the user wants to continue
    continue_testing = (
        input("Do you want to continue with the next test? (y/n): ").strip().lower()
    )
    if continue_testing != "y":
        print("End of tests.")
        break
