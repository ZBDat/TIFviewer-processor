import numpy as np
from scipy.ndimage import gaussian_filter
from pydantic import BaseModel, ConfigDict, Field


class Params(BaseModel):
    sigma: float = Field(default=25.54, gt=0)
    epsilon: float = Field(default=0.08, gt=0)
    output_gain: float = Field(default=1.0, gt=0)
    model_config = ConfigDict(extra="forbid")


def apply(
    image: np.ndarray,
    sigma: float = 25.54,
    epsilon: float = 0.08,
    output_gain: float = 1.0,
) -> np.ndarray:
    """Local contrast normalization.

    For each pixel p:
        p_norm = (p - local_mean) / (local_std + epsilon)

    Parameters
    ----------
    image:       Input 2-D array (uint16 or float32).
    sigma:       Gaussian blur radius for computing local statistics.
    epsilon:     Stability constant added to the local standard deviation.
    output_gain: Multiplicative gain applied to the normalised image before
                 rescaling back to the uint16 range.
    """
    img = image.astype(np.float32)

    local_mean = gaussian_filter(img, sigma=sigma)
    local_mean_sq = gaussian_filter(img ** 2, sigma=sigma)
    local_var = np.maximum(local_mean_sq - local_mean ** 2, 0.0)
    local_std = np.sqrt(local_var)

    normalised = (img - local_mean) / (local_std + epsilon)
    normalised *= output_gain

    # Rescale to [0, 65535] for consistency with the rest of the pipeline
    lo, hi = normalised.min(), normalised.max()
    if hi > lo:
        normalised = (normalised - lo) / (hi - lo) * 65535.0
    else:
        normalised = np.zeros_like(normalised)

    return normalised.astype(np.float32)
