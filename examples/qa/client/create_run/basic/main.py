"""
Basic example showing how to create a test run using the TofuPilotClient.

This script creates a test run for a unit with the specified serial number and part number,
indicating whether the test passed.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""

import random

from tofupilot import TofuPilotClient


def main():
    # Initialize the TofuPilot client.
    client = TofuPilotClient()
    # Create a test run for the unit with serial number "00102" and part
    # number "PCB01"
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"
    client.create_run(
        procedure_id="FVT1",
        unit_under_test={
            "serial_number": serial_number,
            "part_number": "PCB01"},
        run_passed=True,
    )


if __name__ == "__main__":
    main()
