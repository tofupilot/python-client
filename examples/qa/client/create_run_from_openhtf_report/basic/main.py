from openhtf import PhaseResult, Test
from openhtf.output.callbacks import json_factory
from openhtf.plugs import user_input
from tofupilot import TofuPilotClient

client = TofuPilotClient()


# Define a test phase to simulate the power-on procedure
def power_on_test(test):
    print("Power on.")
    return PhaseResult.CONTINUE


# Function to execute the test and save results to a JSON file
def execute_test(file_path):
    test = Test(power_on_test, serial_number="PCB01")

    # Set output callback to save the test results as a JSON file
    test.add_output_callbacks(json_factory.OutputToJSON(file_path))

    # Execute the test with a specific device identifier
    test.execute(lambda: "0001")


def main():
    # Specify the file path for saving test results
    file_path = "./test_result.json"
    execute_test(file_path)

    # Upload the test results to TofuPilot, specifying the importer type
    client.create_run_from_openhtf_report(file_path)


if __name__ == "__main__":
    main()
