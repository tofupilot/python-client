import openhtf as htf
from openhtf import Test, measures
from openhtf.plugs import plug
from openhtf.util import units
from plugs.mock_dut import MockDutPlug
from tofupilot.openhtf import TofuPilot
from utils.calibrate_sensor import calibrate_sensor
from utils.compute_noise_density import compute_noise_density
from utils.compute_r2 import compute_r2
from utils.compute_residuals import compute_residuals
from utils.compute_temp_sensitivity import compute_temp_sensitivity


@plug(dut=MockDutPlug)
def connect_dut(test: Test, dut: MockDutPlug) -> None:
    """Connect to the Device Under Test (DUT)."""
    dut.connect()


@measures(
    *(
        htf.Measurement("{sensor}_noise_density_{axis}")
        .doc("Noise density, normalized to √Hz")
        .in_range(0.0, {"acc": 0.003, "gyro": 0.005}.get(sensor))
        .with_units(
            {
                "acc": units.METRE_PER_SECOND_SQUARED,
                "gyro": units.DEGREE_PER_SECOND,
            }.get(sensor)
        )
        .with_args(sensor=sensor, axis=axis)
        for sensor in ("acc", "gyro")
        for axis in ("x", "y", "z")
    ),
    *(
        htf.Measurement("{sensor}_temp_sensitivity_max_{axis}")
        .doc("Max temperature sensitivity (unit/°C)")
        .with_units(
            {
                "acc": units.METRE_PER_SECOND_SQUARED,
                "gyro": units.DEGREE_PER_SECOND,
            }.get(sensor)
        )
        .with_args(sensor=sensor, axis=axis)
        for sensor in ("acc", "gyro")
        for axis in ("x", "y", "z")
    ),
    *(
        htf.Measurement("{sensor}_temp_sensitivity_ref_{axis}")
        .doc("Temperature sensitivity at 25°C (unit/°C)")
        .in_range(
            {
                "acc": {"x": 5e-4, "y": 5e-4, "z": 5e-4},
                "gyro": {"x": 6e-5, "y": 6e-5, "z": 6e-5},
            }[sensor][axis],
            {
                "acc": {"x": 1e-2, "y": 1e-2, "z": 1e-2},
                "gyro": {"x": 1e0, "y": 1e0, "z": 1e0},
            }[sensor][axis],
        )
        .with_units(
            {
                "acc": units.METRE_PER_SECOND_SQUARED,
                "gyro": units.DEGREE_PER_SECOND,
            }.get(sensor)
        )
        .with_args(sensor=sensor, axis=axis)
        for sensor in ("acc", "gyro")
        for axis in ("x", "y", "z")
    ),
)
@plug(dut=MockDutPlug)
def get_calibration_data(test: Test, dut: MockDutPlug) -> None:
    """Retrieve calibration data from the DUT."""
    test.state.update(dut.get_imu_data(test))

    for sensor, data_key in [("acc", "acc_data"), ("gyro", "gyro_data")]:
        sensor_data = test.state[data_key]
        temperature = sensor_data["temperature"]
        axes_data = {axis: sensor_data[f"{sensor}_{axis}"]
                     for axis in ["x", "y", "z"]}

        for axis, axis_data in axes_data.items():
            noise_density = compute_noise_density(axis_data)
            temp_sensitivity = compute_temp_sensitivity(axis_data, temperature)

            test.measurements[f"{sensor}_noise_density_{axis}"] = noise_density
            test.measurements[f"{sensor}_temp_sensitivity_max_{axis}"] = (
                temp_sensitivity["max_sensitivity"]
            )
            test.measurements[f"{sensor}_temp_sensitivity_ref_{axis}"] = (
                temp_sensitivity["sensitivity_at_ref"]
            )


@measures(
    *(
        htf.Measurement("{sensor}_polynomial_coefficients_{axis}")
        .doc("Calibration polynomial coefficient matrix")
        .with_args(sensor=sensor, axis=axis)
        for sensor in ("acc", "gyro")
        for axis in ("x", "y", "z")
    ),
    *(
        htf.Measurement("{sensor}_residual_mean_{axis}")
        .doc("Residual mean")
        .in_range(0.0, {"acc": 0.01, "gyro": 0.01}.get(sensor))
        .with_units(
            {
                "acc": units.METRE_PER_SECOND_SQUARED,
                "gyro": units.DEGREE_PER_SECOND,
            }.get(sensor)
        )
        .with_args(sensor=sensor, axis=axis)
        for sensor in ("acc", "gyro")
        for axis in ("x", "y", "z")
    ),
    *(
        htf.Measurement("{sensor}_residual_std_{axis}")
        .doc("Residual standard deviation")
        .in_range(0.0, {"acc": 5.0, "gyro": 0.3}.get(sensor))
        .with_units(
            {
                "acc": units.METRE_PER_SECOND_SQUARED,
                "gyro": units.DEGREE_PER_SECOND,
            }.get(sensor)
        )
        .with_args(sensor=sensor, axis=axis)
        for sensor in ("acc", "gyro")
        for axis in ("x", "y", "z")
    ),
    *(
        htf.Measurement("{sensor}_residual_p2p_{axis}")
        .doc("Residual peak-to-peak")
        .in_range(
            0.0,
            {
                "acc": {"x": 15.0, "y": 15.0, "z": 35.0},
                "gyro": {"x": 2.0, "y": 2.0, "z": 2.0},
            }[sensor][axis],
        )
        .with_units(
            {
                "acc": units.METRE_PER_SECOND_SQUARED,
                "gyro": units.DEGREE_PER_SECOND,
            }.get(sensor)
        )
        .with_args(sensor=sensor, axis=axis)
        for sensor in ("acc", "gyro")
        for axis in ("x", "y", "z")
    ),
    *(
        htf.Measurement("{sensor}_r2_{axis}")
        .doc("Coefficient of determination R² (unitless)")
        .in_range(0.5, 1.0)
        .with_args(sensor=sensor, axis=axis)
        for sensor in ("acc", "gyro")
        for axis in ("x", "y", "z")
    ),
)
def compute_sensors_calibration(test: Test) -> None:
    """Perform calibration and metrics computation for both accelerometer and gyroscope."""
    for sensor, data_key, calibration_key in [
        ("acc", "acc_data", "acc_calibration_results"),
        ("gyro", "gyro_data", "gyro_calibration_results"),
    ]:
        sensor_data = test.state[data_key]
        temperature = sensor_data["temperature"]
        axes_data = {axis: sensor_data[f"{sensor}_{axis}"]
                     for axis in ["x", "y", "z"]}

        test.state[calibration_key] = calibrate_sensor(
            (temperature, *axes_data.values()), sensor
        )

        for axis, axis_data in axes_data.items():
            fitted_values = test.state[calibration_key]["fitted_values"][f"{axis}_axis"]
            residuals = compute_residuals(axis_data, fitted_values)
            r2 = compute_r2(axis_data, fitted_values)

            # Update measurements
            test.measurements[f"{sensor}_polynomial_coefficients_{axis}"] = test.state[
                calibration_key]["polynomial_coefficients"][f"{axis}_axis"].tolist()
            test.measurements[f"{sensor}_residual_mean_{axis}"] = abs(
                residuals["mean_residual"]
            )
            test.measurements[f"{sensor}_residual_std_{axis}"] = residuals[
                "std_residual"
            ]
            test.measurements[f"{sensor}_residual_p2p_{axis}"] = residuals[
                "p2p_residual"
            ]
            test.measurements[f"{sensor}_r2_{axis}"] = r2

        for axis, fig in zip(["x", "y", "z"],
                             test.state[calibration_key]["figures"]):
            test.attach(
                f"{sensor}_calibration_figure_{axis}",
                fig.getvalue(),
                "image/png")


@plug(dut=MockDutPlug)
def save_calibration(test: Test, dut: MockDutPlug) -> None:
    """Save calibration data to the DUT."""
    dut.save_accelerometer_calibration(test.state["acc_calibration_results"])
    dut.save_gyroscope_calibration(test.state["gyro_calibration_results"])


def main():
    test = htf.Test(
        connect_dut,
        get_calibration_data,
        compute_sensors_calibration,
        save_calibration,
        procedure_id="FVT1",  # First create procedure in Application
        part_number="PCB01",
    )

    with TofuPilot(test):
        test.execute(lambda: "00001")  # mock operator S/N input


if __name__ == "__main__":
    main()
