import subprocess
import os
import pytest


# This function discovers all Python scripts in the examples directory that are not prefixed with '_'
def discover_example_scripts():
    examples_dir = "examples"
    scripts = []
    for filename in os.listdir(examples_dir):
        # Exclude files that start with '_' or that are not Python scripts
        if filename.endswith(".py") and not filename.startswith("_"):
            scripts.append(os.path.join(examples_dir, filename))
    return scripts


# Parametrize the test to run once for each script
@pytest.mark.parametrize("script_path", discover_example_scripts())
def test_example_script(script_path):
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    assert (
        result.returncode == 0
    ), f"Script {script_path} failed with error: {result.stderr}"
