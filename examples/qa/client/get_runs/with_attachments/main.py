from tofupilot import TofuPilotClient
import requests
from pathlib import Path


def main():
    # First create a run
    client = TofuPilotClient()

    serial_number = "SN00106"

    client.create_run(
        procedure_id="FVT1",
        unit_under_test={"serial_number": serial_number, "part_number": "PCB01"},
        run_passed=True,
        attachments=[
            "qa/client/get_runs/basic/data/temperature-map.png"
        ],  # Update with your file path
    )

    # Then fetch the created run using the serial number
    res = client.get_runs(serial_number=serial_number)
    attachments = res["data"][0]["attachments"]

    # Download and save each attachment next to the script
    for attachment in attachments:
        response = requests.get(attachment["url"])
        response.raise_for_status()

        file_path = Path(__file__).parent / attachment["name"]

        with open(file_path, "wb+") as f:
            f.write(response.content)


if __name__ == "__main__":
    main()
