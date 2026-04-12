import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from skimage.exposure import adjust_gamma


class Params(BaseModel):
    gamma: float = Field(default=1.0, gt=0)
    gain: float = Field(default=1.0, gt=0)
    model_config = ConfigDict(extra="forbid")


def apply(image: np.ndarray, gamma: float = 1.0, gain: float = 1.0) -> np.ndarray:
    img = image.astype(np.float32) / 65535.0
    corrected = adjust_gamma(img, gamma=gamma, gain=gain)
    return (np.clip(corrected, 0.0, 1.0) * 65535.0).astype(np.float32)
