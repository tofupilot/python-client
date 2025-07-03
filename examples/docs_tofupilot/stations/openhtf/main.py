# Before running the script, ensure you have created a station in the TofuPilot interface
# and linked it to the specified procedure ID ("FVT1" in this example).
# You also need to save your API key in an environment variable named "STATION_API_KEY"
# or pass it directly as an argument like this: TofuPilot(test,
# api_key="STATION_API_KEY")


import openhtf as htf
from tofupilot.openhtf import TofuPilot


def phase_one(test):
    return htf.PhaseResult.CONTINUE


def main():
    test = htf.Test(
        phase_one,
        procedure_id="FVT1",  # Create a station in TofuPilot linked to this procedure ID
        part_number="PCBA01",
    )

    # The API key can be set in environment variables or passed directly.
    with TofuPilot(test):
        test.execute(lambda: "PCB1A001")


if __name__ == "__main__":
    main()
