import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class Params(BaseModel):
    sigma: float = Field(default=10.0, gt=0)
    low_gain: float = Field(default=0.5, ge=0.0, le=1.0)
    high_gain: float = Field(default=1.5, ge=1.0, le=5.0)
    model_config = ConfigDict(extra="forbid")


def apply(
    image: np.ndarray,
    sigma: float = 10.0,
    low_gain: float = 0.5,
    high_gain: float = 1.5,
) -> np.ndarray:
    img = image.astype(np.float32)
    img_norm = np.clip(img / 65535.0, 0.0, 1.0)
    log_img = np.log1p(img_norm)

    h, w = log_img.shape
    y = np.arange(h, dtype=np.float32) - (h / 2.0)
    x = np.arange(w, dtype=np.float32) - (w / 2.0)
    yy, xx = np.meshgrid(y, x, indexing="ij")
    freq_distance_sq = yy ** 2 + xx ** 2

    # Gaussian high-pass style transfer function
    high_pass = 1.0 - np.exp(-freq_distance_sq / (2.0 * sigma * sigma))
    transfer = low_gain + (high_gain - low_gain) * high_pass

    freq = np.fft.fftshift(np.fft.fft2(log_img))
    filtered = freq * transfer
    out_log = np.real(np.fft.ifft2(np.fft.ifftshift(filtered)))
    out = np.expm1(out_log)

    out = np.nan_to_num(out, nan=0.0, posinf=1.0, neginf=0.0)
    lo = float(out.min())
    hi = float(out.max())
    if hi > lo:
        out = (out - lo) / (hi - lo)
    else:
        out = np.zeros_like(out)
    return np.clip(out * 65535.0, 0.0, 65535.0).astype(np.float32)
