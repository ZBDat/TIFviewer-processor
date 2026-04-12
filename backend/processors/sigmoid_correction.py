import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from skimage.exposure import adjust_sigmoid


class Params(BaseModel):
    cutoff: float = Field(default=0.5, ge=0.0, le=1.0)
    gain: float = Field(default=10.0, gt=0)
    inv: bool = False
    model_config = ConfigDict(extra="forbid")


def apply(
    image: np.ndarray,
    cutoff: float = 0.5,
    gain: float = 10.0,
    inv: bool = False,
) -> np.ndarray:
    img = image.astype(np.float32) / 65535.0
    corrected = adjust_sigmoid(img, cutoff=cutoff, gain=gain, inv=inv)
    return (np.clip(corrected, 0.0, 1.0) * 65535.0).astype(np.float32)
