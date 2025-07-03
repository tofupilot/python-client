import numpy as np


def compute_temp_sensitivity(
    data: np.ndarray, temperatures: np.ndarray, temp_ref: float = 25
) -> dict:
    """
    Computes temperature sensitivity for sensor data.

    Parameters:
    data (numpy.ndarray): Sensor data.
    temperatures (numpy.ndarray): Corresponding temperatures for the data.
    temp_ref (float): Reference temperature for sensitivity calculations (default: 25°C).

    Returns:
    dict: Maximum sensitivity and sensitivity at reference temperature.

    Use this function to assess how sensor readings change with temperature.
    """
    # Calculate temperature changes between consecutive samples.
    d_temp = np.diff(temperatures)

    # Ignore negligible temperature changes to avoid division errors.
    valid_idx = np.abs(d_temp) > 1e-5

    # Compute data changes and sensitivities for valid temperature changes.
    d_data = np.diff(data)
    sensitivities = d_data[valid_idx] / d_temp[valid_idx]

    # Find the index closest to the reference temperature.
    ref_idx = np.argmin(np.abs(temperatures - temp_ref))

    # Select a range around the reference temperature for averaging.
    ref_range = slice(max(ref_idx - 10, 0),
                      min(ref_idx + 10, len(sensitivities)))

    # Average sensitivities near the reference temperature.
    sensitivity_ref = np.mean(sensitivities[ref_range])

    return {
        "max_sensitivity": np.max(np.abs(sensitivities)),
        "sensitivity_at_ref": abs(sensitivity_ref),
    }
