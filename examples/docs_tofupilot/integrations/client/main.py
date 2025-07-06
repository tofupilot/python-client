from tofupilot import TofuPilotClient


def main():
    client = TofuPilotClient()

    client.create_run(
        procedure_id="FVT1",  # Create the procedure first in the Application
        unit_under_test={
            "serial_number": "PCB1A001",
            "part_number": "PCB1",
        },
        run_passed=True,  # Set the Run status to Pass
    )


if __name__ == "__main__":
    main()
