# Before running the script, ensure you have created a station in the TofuPilot interface
# and linked it to the specified procedure ID ("FVT1" in this example).
# You also need to save your API key in an environment variable named "STATION_API_KEY"
# or pass it directly as an argument like this:
# TofuPilotClient(api_key="STATION_API_KEY")

from datetime import datetime, timedelta

from tofupilot import PhaseOutcome, TofuPilotClient


def phase_one():
    start_time_millis = datetime.now().timestamp() * 1000
    phase = {
        "name": "phase_one",
        "outcome": PhaseOutcome.PASS,
        "start_time_millis": start_time_millis,
        "end_time_millis": start_time_millis + 30 * 1000,  # 30 seconds
    }
    return phase


def main():
    # The API key can be set in environment variables or passed directly.
    client = TofuPilotClient()

    phases = [phase_one()]

    client.create_run(
        procedure_id="FVT1",  # Create a station in TofuPilot linked to this procedure ID
        run_passed=all(
            phase["outcome"] == PhaseOutcome.PASS for phase in phases),
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCBA01"},
        phases=phases,
        duration=timedelta(minutes=1, seconds=45),
    )


if __name__ == "__main__":
    main()
