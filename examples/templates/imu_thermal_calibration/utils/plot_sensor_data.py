import os

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")  # Use 'Agg' backend to avoid GUI operations


def plot_sensor_data(
        temp,
        actual,
        fitted,
        residuals,
        axis_label,
        y_label,
        sensor_type,
        save_path):
    plt.figure(figsize=(10, 8))
    plt.subplot(3, 1, 1)
    plt.plot(temp, actual, label="Actual")
    plt.plot(temp, fitted, label="Fitted")
    plt.title(f"{sensor_type.capitalize()} {axis_label}")
    plt.ylabel(y_label)
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(temp, residuals)
    plt.title("Residuals")
    plt.ylabel("Residual")
    plt.xlabel("Temperature (°C)")

    plt.subplot(3, 1, 3)
    plt.hist(residuals, bins=50)
    plt.title("Residuals Histogram")
    plt.xlabel("Residual")
    plt.ylabel("Frequency")

    plt.tight_layout()
    axis_label_sanitized = axis_label.replace(".", "_")
    fig_file = os.path.join(
        save_path, f"{sensor_type}_{axis_label_sanitized}_calibration.png"
    )
    plt.savefig(fig_file)
    plt.close()

    return fig_file
