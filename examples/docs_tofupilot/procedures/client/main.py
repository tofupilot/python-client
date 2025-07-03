from datetime import timedelta

from tofupilot import TofuPilotClient


def main():
    client = TofuPilotClient()

    client.create_run(
        procedure_id="FVT1",  # Create the procedure first in the Application
        run_passed=True,
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCB1"},
        duration=timedelta(minutes=1, seconds=45),
    )


if __name__ == "__main__":
    main()
