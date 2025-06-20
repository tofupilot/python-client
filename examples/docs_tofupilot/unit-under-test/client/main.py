from tofupilot import TofuPilotClient


def main():
    client = TofuPilotClient()

    phases = []

    client.create_run(
        procedure_id="FVT1",  # Create the procedure first in the Application
        unit_under_test={
            "serial_number": "PCB1A002",
            "part_number": "PCB1",
            "revision": "A",  # optional
            "batch_number": "12-24",  # optional
        },
        phases=phases,
        run_passed=True,
    )


if __name__ == "__main__":
    main()
