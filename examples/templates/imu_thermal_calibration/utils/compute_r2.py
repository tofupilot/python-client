import numpy as np


def compute_r2(data: np.ndarray, fit_model: np.ndarray) -> float:
    """
    Computes R-squared to evaluate how well a model fits the data.

    Parameters:
    data (numpy.ndarray): Sensor data.
    fit_model (numpy.ndarray): Fitted model values for the data.

    Returns:
    float: R-squared value.

    Use this function to quantify the goodness-of-fit of the calibration model.
    """
    # Residuals: differences between data and model.
    residuals = data - fit_model

    # Total variation in the data.
    total_variation = np.sum((data - np.mean(data)) ** 2)

    # Variation not explained by the model.
    residual_variation = np.sum(residuals**2)

    # R²: fraction of variance explained by the model.
    r2 = 1 - residual_variation / total_variation
    return r2
