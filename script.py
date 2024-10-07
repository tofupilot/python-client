import pytest
import serial  # Make sure to have pyserial installed (pip install pyserial)
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="module")
def serial_connection():
    """
    Fixture to initialize and close the serial connection.
    This fixture has a 'module' scope, so it is called only once per test module.
    """
    # Create a mock for the serial.Serial object
    with patch("serial.Serial") as mock_serial:
        # Simulate the Serial object and its methods
        mock_instance = MagicMock()
        mock_serial.return_value = mock_instance

        # Set default behaviors for the methods
        mock_instance.readline.return_value = b"OK\n"  # Default value for readline

        yield mock_instance
        # The mock is automatically removed after the tests


@pytest.fixture
def reset_device(serial_connection):
    """
    Fixture to reset the state of the device before each test.
    """
    # Specific command to reset the device
    serial_connection.write(b"RESET\n")
    # Wait for the device to be ready after the reset
    serial_connection.flush()
    yield
    # Add additional code if needed after each test


def test_device_communication(serial_connection):
    """
    Basic test to check communication with the device.
    """
    serial_connection.write(b"STATUS\n")
    response = serial_connection.readline()
    assert response == b"OK\n", f"Unexpected response from the device: {response}"


def test_device_read_data(reset_device, serial_connection):
    """
    Test to read specific data from the device.
    Uses the 'reset_device' fixture to ensure the device is in a known state.
    """
    serial_connection.write(b"READ DATA\n")
    serial_connection.readline.return_value = (
        b"DATA: 12345\n"  # Simulate a specific response
    )
    response = serial_connection.readline()
    assert response.startswith(b"DATA:"), f"Incorrect data received: {response}"


def test_device_send_command(reset_device, serial_connection):
    """
    Test to send a specific command to the device and check the response.
    """
    serial_connection.write(b"COMMAND X\n")
    serial_connection.readline.return_value = (
        b"COMMAND X EXECUTED\n"  # Simulate the appropriate response
    )
    response = serial_connection.readline()
    assert (
        response == b"COMMAND X EXECUTED\n"
    ), f"Command not executed correctly: {response}"


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """
    Hook to perform actions before the start of the test session.
    """
    print("Starting tests for the hardware test bench...")


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    Hook to perform actions after the end of the test session.
    """
    print("Tests completed for the hardware test bench.")
    if exitstatus == 0:
        print("All tests passed successfully.")
    else:
        print(f"Errors occurred: Exit code {exitstatus}")
