import numpy as np


def compute_noise_density(data: np.ndarray, sampling_rate: int = 100) -> float:
    """
    Computes noise density for sensor data.

    Parameters:
    data (numpy.ndarray): Raw sensor data.
    sampling_rate (int): Sensor sampling rate in Hz.

    Returns:
    float: Noise density in units/sqrt(Hz).
    """
    # Use the first 50 samples for noise analysis.
    initial_samples = data[:50]

    # Remove DC offset by subtracting the mean.
    detrended_data = initial_samples - np.mean(initial_samples)

    # Compute noise standard deviation.
    noise_std = np.std(detrended_data)

    # Normalize noise to the frequency domain.
    noise_density = noise_std / np.sqrt(sampling_rate)

    return noise_density
