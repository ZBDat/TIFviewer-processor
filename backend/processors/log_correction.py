import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from skimage.exposure import adjust_log


class Params(BaseModel):
    gain: float = Field(default=1.0, gt=0)
    inv: bool = False
    model_config = ConfigDict(extra="forbid")


def apply(image: np.ndarray, gain: float = 1.0, inv: bool = False) -> np.ndarray:
    img = image.astype(np.float32) / 65535.0
    corrected = adjust_log(img, gain=gain, inv=inv)
    return (np.clip(corrected, 0.0, 1.0) * 65535.0).astype(np.float32)
