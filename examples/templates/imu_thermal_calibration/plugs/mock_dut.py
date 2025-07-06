import time
from pathlib import Path
from typing import Dict

from openhtf import Test
from openhtf.plugs import BasePlug
from pandas import DataFrame, read_csv


class MockDutPlug(BasePlug):
    """
    A mock plug for simulating communication with a DUT.

    Provides methods to connect, disconnect, and save calibration data for the DUT.
    """

    def connect(self) -> None:
        self.logger.info("Simulated: Connecting to DUT.")
        time.sleep(1)

    def disconnect(self) -> None:
        self.logger.info("Simulated: Disconnecting from DUT.")
        time.sleep(1)

    @staticmethod
    def get_imu_data(test: Test) -> Dict:
        data = read_csv("data/imu_raw_data.csv", delimiter="\t")
        test.attach("raw_calibration_data", data.to_csv(), "text/csv")
        return {
            "acc_data": {
                "temperature": data["imu.temperature"],
                "acc_x": data["imu.acc.x"],
                "acc_y": data["imu.acc.y"],
                "acc_z": data["imu.acc.z"]
                - 9.80600,  # Acceleration of freefall in Switzerland zone 2
            },
            "gyro_data": {
                "temperature": data["imu.temperature"],
                "gyro_x": data["imu.gyro.x"],
                "gyro_y": data["imu.gyro.y"],
                "gyro_z": data["imu.gyro.z"],
            },
        }

    def save_accelerometer_calibration(
            self, polynomial_coefficients: dict) -> None:
        self.logger.info("Simulated: Saving IMU thermal calibration to DUT.")
        time.sleep(0.5)

    def save_gyroscope_calibration(
            self, polynomial_coefficients: dict) -> None:
        self.logger.info("Simulated: Saving IMU thermal calibration to DUT.")
        time.sleep(0.5)

    def tearDown(self) -> None:
        """
        OpenHTF automatically calls the tearDown method after the test phase ends.
        This ensures that any required cleanup (like disconnecting from the DUT) is performed.
        """
        self.logger.info("Simulated: Performing teardown.")
        self.disconnect()
