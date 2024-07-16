import subprocess
import os

# This functions automatically executes and tests all python scripts found in examples directory
def test_examples():
    for filename in os.listdir('examples'):
        if filename.endswith('.py'):
            script_path = os.path.join('examples', filename)
            result = subprocess.run(['python', script_path], capture_output=True, text=True)
            assert result.returncode == 0, f"Script {filename} failed with error: {result.stderr}"