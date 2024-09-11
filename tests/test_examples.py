import subprocess
import os
import pytest


# This function discovers all Python scripts in the examples directory
def discover_example_scripts():
    examples_dir = "examples"
    scripts = []
    for filename in os.listdir(examples_dir):
        if filename.endswith(".py"):
            scripts.append(os.path.join(examples_dir, filename))
    return scripts


# Parametrize the test to run once for each script
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
