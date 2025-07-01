import numpy as np


def compute_residuals(data: np.ndarray, fit_model: np.ndarray) -> dict:
    """
    Computes residuals between sensor data and a fitted model.

    Parameters:
    data (numpy.ndarray): Sensor data.
    fit_model (numpy.ndarray): Fitted model values for the same data.

    Returns:
    dict: Mean, standard deviation, and peak-to-peak residuals.

    Use this function to evaluate calibration quality by analyzing deviations.
    """
    # Residuals: differences between data and model.
    residuals = data - fit_model

    return {
        # Mean residual: measures systematic error.
        "mean_residual": np.mean(residuals),
        # Standard deviation: indicates scatter.
        "std_residual": np.std(residuals),
        # Peak-to-peak: captures extreme errors.
        "p2p_residual": np.ptp(residuals),
    }
