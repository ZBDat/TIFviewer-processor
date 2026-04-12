import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from skimage.exposure import rescale_intensity as sk_rescale_intensity


class Params(BaseModel):
    in_low: int = Field(default=0, ge=0, le=65535)
    in_high: int = Field(default=65535, ge=0, le=65535)
    out_low: int = Field(default=0, ge=0, le=65535)
    out_high: int = Field(default=65535, ge=0, le=65535)
    model_config = ConfigDict(extra="forbid")


def apply(
    image: np.ndarray,
    in_low: int = 0,
    in_high: int = 65535,
    out_low: int = 0,
    out_high: int = 65535,
) -> np.ndarray:
    if in_low >= in_high or out_low >= out_high:
        raise ValueError("invalid intensity range")

    img = image.astype(np.float32)
    rescaled = sk_rescale_intensity(
        img,
        in_range=(float(in_low), float(in_high)),
        out_range=(float(out_low), float(out_high)),
    )
    return np.clip(rescaled, 0.0, 65535.0).astype(np.float32)
