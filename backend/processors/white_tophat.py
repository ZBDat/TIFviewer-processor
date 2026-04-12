import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from scipy.ndimage import grey_opening


class Params(BaseModel):
    size: int = Field(default=15, ge=1, le=511)
    model_config = ConfigDict(extra="forbid")


def apply(image: np.ndarray, size: int = 15) -> np.ndarray:
    img = image.astype(np.float32)
    opened = grey_opening(img, size=(size, size))
    result = img - opened
    return np.clip(result, 0.0, 65535.0).astype(np.float32)
