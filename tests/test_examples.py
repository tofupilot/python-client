import os
import subprocess
from collections.abc import Iterator

import pytest


# This function discovers all Python scripts in the examples directory that are not prefixed with '_'
def discover_example_scripts() -> Iterator[str]:
    examples_dir = "examples"
    for filename in os.listdir(examples_dir):
        # Exclude files that start with '_' or that are not Python scripts
        if filename.endswith(".py") and not filename.startswith("_"):
            yield os.path.join(examples_dir, filename)


# Parametrize the test to run once for each script
@pytest.mark.skipif(not os.getenv("TOFUPILOT_API_KEY"), reason="TOFUPILOT_API_KEY is not set")
@pytest.mark.parametrize("script_path", discover_example_scripts())
def test_example_script(script_path):
    # Run the script and capture the output
    result = subprocess.run(["python", script_path], capture_output=True, text=True)

    # Check if the script ran successfully by return code
    assert (
        result.returncode == 0
    ), f"Script {script_path} failed with return code {result.returncode} and error: {result.stderr}"

    # Check if stderr is not empty
    assert not result.stderr.strip(), f"Error in stderr: {result.stderr}"
