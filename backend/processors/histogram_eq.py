import numpy as np
from skimage.exposure import equalize_hist
from pydantic import BaseModel, ConfigDict


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")


def apply(image: np.ndarray) -> np.ndarray:
    """Histogram equalization on a 16-bit grayscale image.

    The image is normalised to [0, 1] before equalisation, then scaled back
    to the uint16 range so that downstream processors continue to work on a
    consistent data type.
    """
    img_float = image.astype(np.float32) / 65535.0
    equalised = equalize_hist(img_float)          # returns float in [0, 1]
    return (equalised * 65535.0).astype(np.float32)
