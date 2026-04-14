import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from scipy.ndimage import uniform_filter


class Params(BaseModel):
    radius: int = Field(default=8, ge=1, le=128)
    epsilon: float = Field(default=0.01, gt=0)
    model_config = ConfigDict(extra="forbid")


def _box_filter(img: np.ndarray, radius: int) -> np.ndarray:
    size = 2 * radius + 1
    return uniform_filter(img, size=size, mode="reflect")


def apply(
    image: np.ndarray,
    radius: int = 8,
    epsilon: float = 0.01,
) -> np.ndarray:
    i = np.clip(image.astype(np.float32) / 65535.0, 0.0, 1.0)
    p = i

    mean_i = _box_filter(i, radius)
    mean_p = _box_filter(p, radius)
    corr_i = _box_filter(i * i, radius)
    corr_ip = _box_filter(i * p, radius)

    var_i = corr_i - mean_i * mean_i
    cov_ip = corr_ip - mean_i * mean_p

    a = cov_ip / (var_i + epsilon)
    b = mean_p - a * mean_i

    mean_a = _box_filter(a, radius)
    mean_b = _box_filter(b, radius)
    q = mean_a * i + mean_b

    return np.clip(q * 65535.0, 0.0, 65535.0).astype(np.float32)
