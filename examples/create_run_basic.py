from tofupilot import TofuPilotClient

client = TofuPilotClient()

client.create_run(
    procedure_id="FVT1",
    unit_under_test={
      "serial_number": "00102",
      "part_number": "PCB01"
    },
    run_passed=True,
)
