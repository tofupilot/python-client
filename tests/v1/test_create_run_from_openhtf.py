# Adapted from https://github.com/tofupilot/examples/blob/5cf044d0e55c11ea55114014edb206605689aa6d/qa/client/create_run_from_openhtf_report/basic/main.py

from openhtf import PhaseResult, Test as Openhtf_Test, measures # Otherwise conflicts with pytest
from openhtf.core import measurements
from openhtf.output.callbacks import json_factory
from tofupilot import TofuPilotClient

from .utils import client

# Define a test phase to simulate the power-on procedure
def power_on_test(test):
    print("Power on.")
    return PhaseResult.CONTINUE

def test_basic(client: TofuPilotClient, procedure_identifier):
    # Specify the file path for saving test results
    file_path = "./test_result.json"

    test = Openhtf_Test(power_on_test, serial_number="PCB01", procedure_id=procedure_identifier, part_number="test_basic")

    # Set output callback to save the test results as a JSON file
    test.add_output_callbacks(json_factory.OutputToJSON(file_path))

    # Execute the test with a specific device identifier
    test.execute(lambda: "0001")

    # Upload the test results to TofuPilot, specifying the importer type
    assert client.create_run_from_openhtf_report(file_path)

# Adapted from https://github.com/tofupilot/examples/blob/5cf044d0e55c11ea55114014edb206605689aa6d/qa/client/create_run_from_openhtf_report/with_attachments/main.py


# Define a phase that attaches a file
def phase_file_attachment(test):
    test.attach_from_file("attachments/sample_file.txt")
    test.attach_from_file("attachments/oscilloscope.jpeg")
    return PhaseResult.CONTINUE

def test_with_attachments(client: TofuPilotClient, procedure_identifier):
    # Specify the file path for saving test results
    file_path = "./test_result2.json"
    
    test = Openhtf_Test(
        power_on_test,
        phase_file_attachment,
        procedure_id=procedure_identifier,
        part_number="test_with_attachments",
        serial_number="PCB01")

    # Set output callback to save the test results as a JSON file
    test.add_output_callbacks(json_factory.OutputToJSON(file_path))

    # Execute the test with a specific device identifier
    test.execute(lambda: "0001")

    # Upload the test results to TofuPilot, specifying the importer type
    assert client.create_run_from_openhtf_report(file_path)

# Multi-dimensional measurement test based on OpenHTF examples
@measures(
    measurements.Measurement('power_time_series').with_dimensions('time_ms', 'voltage', 'current'),
    measurements.Measurement('temperature_profile').with_dimensions('sensor_id', 'reading_number'),
    measurements.Measurement('frequency_response').with_dimensions('frequency_hz'),
    measurements.Measurement('average_power').with_units('W'),
    measurements.Measurement('max_temperature').with_units('°C'),
    measurements.Measurement('test_duration').with_units('ms')
)
def multidimensional_measurement_phase(test):
    """Phase that demonstrates multi-dimensional measurements from OpenHTF."""
    
    # Multi-dimensional power measurements over time
    # Simulate power measurements at different time points with varying voltage and current
    for i in range(5):
        time_ms = i * 100  # 0, 100, 200, 300, 400 ms
        voltage = 12.0 + (i * 0.5)  # 12.0, 12.5, 13.0, 13.5, 14.0 V
        current = 2.0 + (i * 0.1)   # 2.0, 2.1, 2.2, 2.3, 2.4 A
        
        # Set multi-dimensional measurement with 3 dimensions
        dimensions = (time_ms, voltage, current)
        test.measurements['power_time_series'][dimensions] = voltage * current
    
    # Multi-dimensional temperature measurements from multiple sensors
    sensor_names = ['CPU_TEMP', 'GPU_TEMP', 'AMBIENT_TEMP']
    for sensor_id in sensor_names:
        for reading_num in range(3):
            # Simulate different temperature patterns for each sensor
            if sensor_id == 'CPU_TEMP':
                temp = 45.0 + reading_num * 5.0  # 45, 50, 55°C
            elif sensor_id == 'GPU_TEMP':
                temp = 40.0 + reading_num * 3.0  # 40, 43, 46°C
            else:  # AMBIENT_TEMP
                temp = 22.0 + reading_num * 1.0  # 22, 23, 24°C
            
            test.measurements['temperature_profile'][(sensor_id, reading_num)] = temp
    
    # Single-dimensional array: frequency response measurements
    frequencies = [100.0, 1000.0, 10000.0, 100000.0]  # Hz
    responses = [0.95, 0.98, 0.85, 0.60]  # Response ratios
    
    for freq, response in zip(frequencies, responses):
        test.measurements['frequency_response'][freq] = response
    
    # Calculate summary measurements from multi-dimensional data
    power_measurements = test.measurements['power_time_series']
    if power_measurements.is_value_set:
        # Extract power values and calculate average
        power_values = [measurement[-1] for measurement in power_measurements.value]
        test.measurements['average_power'] = sum(power_values) / len(power_values)
    
    # Find maximum temperature across all sensors
    temp_measurements = test.measurements['temperature_profile']
    if temp_measurements.is_value_set:
        temp_values = [measurement[-1] for measurement in temp_measurements.value]
        test.measurements['max_temperature'] = max(temp_values)
    
    # Record test duration
    test.measurements['test_duration'] = 500  # ms
    
    return PhaseResult.CONTINUE


def test_multidimensional_measurements(client: TofuPilotClient, procedure_identifier):
    """Test OpenHTF with multi-dimensional measurements upload to TofuPilot."""
    # Specify the file path for saving test results
    file_path = "./test_multidim_result.json"
    
    test = Openhtf_Test(
        power_on_test,
        multidimensional_measurement_phase,
        procedure_id=procedure_identifier,
        part_number="test_multidim",
        serial_number="MULTIDIM_PCB_001"
    )

    # Set output callback to save the test results as a JSON file
    test.add_output_callbacks(json_factory.OutputToJSON(file_path))

    # Execute the test with a specific device identifier
    test.execute(lambda: "MULTIDIM_001")

    # Upload the test results to TofuPilot, specifying the importer type
    assert client.create_run_from_openhtf_report(file_path)