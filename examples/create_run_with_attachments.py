from tofupilot import TofuPilotClient

client = TofuPilotClient()


def test_function():
    # test status
    run_passed = True
    # local path to attachements
    attachments = [
        "data/temperature-map.png",  # path to your local files
        "data/performance-report.pdf",
    ]
    return run_passed, attachments


run_passed, attachments = test_function()

response = client.create_run(
    procedure_id="FVT1",
    unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
    run_passed=run_passed,
    attachments=attachments,
)

success = response.get("success")

assert success
