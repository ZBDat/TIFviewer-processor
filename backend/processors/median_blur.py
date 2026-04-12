import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from scipy.ndimage import median_filter


class Params(BaseModel):
    size: int = Field(default=3, ge=1, le=255)
    model_config = ConfigDict(extra="forbid")


def apply(image: np.ndarray, size: int = 3) -> np.ndarray:
    img = image.astype(np.float32)
    filtered = median_filter(img, size=size)
    return np.clip(filtered, 0.0, 65535.0).astype(np.float32)
