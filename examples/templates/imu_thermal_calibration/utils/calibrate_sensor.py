from io import BytesIO
from typing import Dict, List, Tuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")


def calibrate_sensor(
    data: Tuple[List[float], List[float], List[float], List[float]],
    sensor: str,
    polynomial_order: int = 3,
) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Fit a polynomial model to the sensor data against temperature.

    Args:
    data (tuple): A tuple containing:
    - temperature data (numpy array)
    - sensor data for each axis (numpy arrays for x, y, z)
    polynomial_order (int): The degree of the polynomial to fit.

    Returns:
    dict: A dictionary containing:
    - polynomial_coefficients: Coefficients of the fitted polynomial for each axis.
    - fitted_values: Fitted values for each axis at the given temperature points.
    - figures: Matplotlib figure objects as in-memory images for each axis.
    """

    # Define color names
    colors = {
        "zinc": "#09090B",
        "white": "#ffffff",
        "lime": "#bef264",
        "pink": "#f9a8d4",
    }

    # Convert the tuple elements to NumPy arrays
    temp, *sensor_data = (np.array(arr) for arr in data)

    poly_coeffs: Dict[str, np.ndarray] = {}
    fitted_values: Dict[str, np.ndarray] = {}
    figures: List[BytesIO] = []
    axis_list = ("x", "y", "z")

    for i, axis_data in enumerate(sensor_data):
        if sensor == "acc":
            sensor_name = "Accelerometer"
            unit = "m/s²"
        else:
            sensor_name = "Gyroscope"
            unit = "°/s"
        axis_name = f"{axis_list[i]}_axis"

        # Fit polynomial to the data
        coeffs = np.polyfit(temp, axis_data, polynomial_order)
        poly_coeffs[axis_name] = coeffs

        # Compute fitted values
        fitted = np.polyval(coeffs, temp)
        fitted_values[axis_name] = fitted

        # Calculate residuals
        residuals = axis_data - fitted

        # Generate plot and store figure
        fig, axs = plt.subplots(
            2, 1, figsize=(8, 10), gridspec_kw={"height_ratios": [3, 1]}
        )
        fig.patch.set_facecolor(colors["zinc"])
        axs[0].set_facecolor(colors["zinc"])
        axs[1].set_facecolor(colors["zinc"])

        # Plot sensor data with the fitted curve
        axs[0].plot(
            temp,
            axis_data,
            ".",
            color=colors["lime"],
            label=f"{sensor_name} data")
        axs[0].plot(
            temp,
            fitted,
            "-",
            color=colors["pink"],
            label="Fitted Curve")
        axs[0].set_title(
            f"{sensor_name} {axis_name[0].capitalize()} axis calibration",
            color=colors["white"],
        )
        axs[0].set_xlabel("Temperature (°C)", color=colors["white"])
        axs[0].set_ylabel(
            f"{sensor_name} value ({unit})",
            color=colors["white"])
        axs[0].tick_params(colors=colors["white"])
        axs[0].spines["bottom"].set_color(colors["white"])
        axs[0].spines["left"].set_color(colors["white"])
        axs[0].spines["top"].set_color(colors["white"])
        axs[0].spines["right"].set_color(colors["white"])
        axs[0].legend(
            facecolor=colors["zinc"],
            edgecolor=colors["white"],
            labelcolor=colors["white"],
        )

        # Plot histogram of residuals
        axs[1].hist(
            residuals,
            bins=30,
            color=colors["lime"],
            edgecolor=colors["white"],
            alpha=0.8,
        )
        axs[1].set_title(
            f"Residual distribution ({sensor_name.lower()} {axis_name[0].capitalize()} axis)",
            color=colors["white"],
        )
        axs[1].set_xlabel(f"Residual value ({unit})", color=colors["white"])
        axs[1].set_ylabel("Occurences", color=colors["white"])
        axs[1].tick_params(colors=colors["white"])
        axs[1].spines["bottom"].set_color(colors["white"])
        axs[1].spines["left"].set_color(colors["white"])
        axs[1].spines["top"].set_color(colors["white"])
        axs[1].spines["right"].set_color(colors["white"])

        # Add spacing between subplots
        plt.subplots_adjust(hspace=0.3)

        # Convert the figure to an in-memory image
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        figures.append(buffer)
        plt.close(fig)

    return {
        "polynomial_coefficients": poly_coeffs,
        "fitted_values": fitted_values,
        "figures": figures,
    }
