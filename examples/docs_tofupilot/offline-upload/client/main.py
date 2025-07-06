from datetime import datetime, timedelta

from tofupilot import TofuPilotClient


def main():
    client = TofuPilotClient()

    client.create_run(
        procedure_id="FVT1",  # Create the procedure first in the Application
        started_at=datetime.now() - timedelta(days=1),  # Run performed the day before
        unit_under_test={
            "serial_number": "PCB1A003",
            "part_number": "PCB1",
        },
        run_passed=True,
    )


if __name__ == "__main__":
    main()
