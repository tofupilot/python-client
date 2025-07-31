"""Test runner for examples from GitHub repository."""

import os
import shutil
import subprocess
import sys
import tempfile
import logging
import re
from pathlib import Path
from typing import List, Dict, Any

import pytest


# Global variable to store the repo path
_EXAMPLES_REPO_PATH = None

def _get_examples_repo():
    """Get or create the examples repository."""
    global _EXAMPLES_REPO_PATH
    if _EXAMPLES_REPO_PATH is None:
        repo_url = "https://github.com/tofupilot/examples.git"

        # Create a temporary directory, deleted by teardown
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir) / "examples"
        
        # Clone the example repo into it
        result = subprocess.run(
            ["git", "clone", repo_url, str(repo_path)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError("failed to clone example repository")
        
        _EXAMPLES_REPO_PATH = repo_path
    
    return _EXAMPLES_REPO_PATH


@pytest.fixture(scope="session")
def teardown():
    yield
    
    # Delete the temporary directory
    global _EXAMPLES_REPO_PATH
    if _EXAMPLES_REPO_PATH:
        shutil.rmtree(_EXAMPLES_REPO_PATH.parent)
        _EXAMPLES_REPO_PATH = None


def pytest_generate_tests(metafunc):
    """Generate test parameters for each GitHub example file."""
    if "example_file" in metafunc.fixturenames:
        repo_path = _get_examples_repo()

        python_files = list((repo_path / "testing_examples" / "openhtf").rglob("*.py"))

        # Paths that will be printed by pytest after the testname: 
        #                        v here
        # ...test_github_example[testing_examples/openhtf/without_streaming/main.py]
        human_readable_paths = [f.relative_to(repo_path).as_posix() for f in python_files]

        metafunc.parametrize("example_file", python_files, ids=human_readable_paths)

@pytest.fixture(autouse=True)
def no_error_logs(caplog):
    yield
    errors = [record for record in caplog.get_records('call') if record.levelno >= logging.ERROR]
    assert not errors, f"{errors[0].message}"
    
def test_github_example(teardown, tofupilot_server_url, api_key, procedure_identifier, example_file: Path, tmp_path):
    """Test individual Python example from the GitHub repository."""

    assert example_file.exists(), f"Example file not found: {example_file}"
    
    with open(example_file, 'r') as f:
        filedata = f.read()

    # Add url to example
    (filedata, n_modifications) = re.subn(r'with TofuPilot\(([\w, =]*)\)', lambda m: f'with TofuPilot({m.group(1)}, url="{tofupilot_server_url}")', filedata)
    assert n_modifications == 1, "Failed to update url"

    # Add API key to TofuPilot constructor
    # Pattern 1: TofuPilot(test)
    (filedata, n_modifications) = re.subn(r'TofuPilot\(test\)', f'TofuPilot(test, api_key="{api_key}")', filedata)
    
    # Pattern 2: TofuPilot(test, stream=False)
    if n_modifications == 0:
        (filedata, n_modifications) = re.subn(r'TofuPilot\(test, stream=False\)', f'TofuPilot(test, stream=False, api_key="{api_key}")', filedata)
    
    # Pattern 3: TofuPilot(test, stream=True)
    if n_modifications == 0:
        (filedata, n_modifications) = re.subn(r'TofuPilot\(test, stream=True\)', f'TofuPilot(test, stream=True, api_key="{api_key}")', filedata)

    # Update procedure identifier to one present at that url
    (filedata, n_modifications) = re.subn(r'procedure_id="\w+"', f'procedure_id="{procedure_identifier}"', filedata)
    assert n_modifications == 1, "Failed to update procedure_id"

    # Create temporary file so that the errors are reported on the modified file
    modified_file_path = tmp_path / "main.py"
    modified_file_path.write_text(filedata, encoding="utf-8")

    # Copy any data files that might be needed
    example_dir = example_file.parent
    data_dir = example_dir / "data"
    if data_dir.exists():
        # Copy data directory to tmp_path
        shutil.copytree(data_dir, tmp_path / "data")

    # Change to the directory where the example is run so relative paths work
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        
        # Run the modified example file
        code = compile(filedata, str(modified_file_path), 'exec')
        exec(code, {'__file__': str(modified_file_path), '__name__': '__main__'})
    finally:
        os.chdir(original_cwd)