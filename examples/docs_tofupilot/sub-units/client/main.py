from tofupilot import TofuPilotClient

# Please ensure both units PCB1A001 and LEN1A001 exist before running this script
# Refer to https://tofupilot.com/docs/procedures for an example on how to
# create them


def main():
    client = TofuPilotClient()

    client.create_run(
        procedure_id="FVT2",  # Create the procedure first in the Application
        unit_under_test={"serial_number": "CAM1A001", "part_number": "CAM1"},
        run_passed=True,
        sub_units=[{"serial_number": "PCB1A001"},
                   {"serial_number": "LEN1A001"}],
    )


if __name__ == "__main__":
    main()
