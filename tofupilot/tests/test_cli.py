import sys
import subprocess
from importlib.metadata import (
    version,
)


def test_version():
    current_version = version("tofupilot")

    result = subprocess.run(
        [sys.executable, "tofupilot/cli.py", "--version"],
        stdout=subprocess.PIPE,  # Capture the standard output
        stderr=subprocess.PIPE,  # Capture standard error
        text=True,
    )

    assert result.stdout.strip() == f"TofuPilot {current_version}"
