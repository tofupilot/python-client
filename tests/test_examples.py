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
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    assert (
        result.returncode == 0
    ), f"Script {script_path} failed with error: {result.stderr}"
