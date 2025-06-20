import random
from datetime import datetime, timedelta

from tofupilot import TofuPilotClient

client = TofuPilotClient()


def handle_test():
    # Create 2 test for same SN
    for testnumber in range(2):
        client.create_run(
            procedure_id="FVT112",
            started_at=datetime.now(),
            unit_under_test={
                "part_number": "FPY",
                "serial_number": "FPY-0123410",
            },
            # First Good, Second KO, to check FPY
            run_passed=True if testnumber == 0 else False,
        )


if __name__ == "__main__":
    handle_test()
