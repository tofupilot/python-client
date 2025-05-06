# TofuPilot OpenHTF Integration

This module provides integration between OpenHTF and TofuPilot, enhancing the testing experience with features like:

- Automatic uploading of test results to TofuPilot
- Real-time streaming of test execution
- Enhanced user prompts with TofuPilot operator URLs displayed in the console
- Graceful error handling for test interruptions

## Quick Start

```python
from openhtf import Test
from tofupilot.openhtf import TofuPilot, execute_with_graceful_exit

def main():
    test = Test(*your_phases, procedure_id="FVT1")

    # Stream real-time test execution data to TofuPilot
    with TofuPilot(test):
        # Use helper function for graceful Ctrl+C handling
        result = execute_with_graceful_exit(test, test_start=lambda: "SN15")
        
        if result is None:
            print("Test was interrupted. Exiting gracefully.")
        else:
            print(f"Test completed with outcome: {result.outcome.name}")
```

## Enhanced Prompt Functionality

TofuPilot enhances OpenHTF's prompt system by displaying the TofuPilot URL before each prompt.

### URL Display

The TofuPilot URL is displayed clearly in the console before each prompt:
```
📱 View live test results: https://tofupilot.example.com/test/123
Enter a DUT ID in order to start the test.
```

This URL display is kept separate from the actual prompt text to maintain clean prompts in the web UI.

### Using Enhanced Prompts

There are two main ways to use the enhanced prompts:

1. **Use the provided prompt functions**:
   ```python
   from tofupilot.openhtf import prompt_with_tofupilot_url
   
   response = prompt_with_tofupilot_url(
       "Enter calibration value:",
       operator_page_url="https://tofupilot.example.com/test/123"
   )
   ```

2. **Use the `patch_openhtf_prompts` function** to enhance all OpenHTF prompts:
   ```python
   from tofupilot.openhtf import patch_openhtf_prompts
   
   # Call this early in your application
   patch_openhtf_prompts(tofupilot_url="https://tofupilot.example.com/test/123")
   ```

## Graceful Error Handling

TofuPilot provides a helper function to gracefully handle interruptions during test execution.

### Using execute_with_graceful_exit

```python
from tofupilot.openhtf import execute_with_graceful_exit

# Inside your with TofuPilot(test) block:
result = execute_with_graceful_exit(test, test_start=your_test_start_fn)

# Only show success message if test wasn't interrupted
if result is not None:
    print(f"Test completed with outcome: {result.outcome.name}")
```

This helper:
- Shows immediate feedback when Ctrl+C is pressed
- Displays "Test execution interrupted by user. Test was interrupted. Exiting gracefully."
- Properly handles KeyboardInterrupt exceptions
- Returns None if the test was interrupted
- Ensures clean resource release
- Prevents stack traces from appearing when the user presses Ctrl+C

## OpenHTF Output Callbacks

By default, the TofuPilot context manager automatically adds an output callback to upload test results to TofuPilot upon test completion:

```python
with TofuPilot(test):
    # This will automatically upload test results when complete
    test.execute(test_start=lambda: "SN15")
```

If you want to manually add the callback:

```python
from tofupilot.openhtf import upload

test = Test(*your_phases)
test.add_output_callbacks(upload())
test.execute(test_start=lambda: "SN15")
```

## Important Notes

1. TofuPilot URL information is displayed in the console log, not in the prompt itself.
2. When using `execute_with_graceful_exit`, interrupted tests will return `None` instead of a test result.
3. The TofuPilot context manager handles automatic upload of test results.
4. For OpenHTF tests that are interrupted, the standard OpenHTF output callbacks will still run.