import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from scipy.ndimage import gaussian_filter


class Params(BaseModel):
    sigma: float = Field(default=1.5, gt=0)
    model_config = ConfigDict(extra="forbid")


def apply(image: np.ndarray, sigma: float = 1.5) -> np.ndarray:
    img = image.astype(np.float32)
    blurred = gaussian_filter(img, sigma=sigma)
    return np.clip(blurred, 0.0, 65535.0).astype(np.float32)
