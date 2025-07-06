from tofupilot import TofuPilotClient


def phase_file_attachment():
    file_paths = ["data/temperature-map.png"]  # Replace with your files paths
    return file_paths


def main():
    client = TofuPilotClient()

    attachments = phase_file_attachment()

    client.create_run(
        procedure_id="FVT1",  # Create the procedure first in the Application
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCB1"},
        run_passed=True,
        attachments=attachments,
    )


if __name__ == "__main__":
    main()
