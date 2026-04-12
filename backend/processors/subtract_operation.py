import numpy as np
from pydantic import BaseModel, ConfigDict


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")


def apply(upper: np.ndarray, lower: np.ndarray) -> np.ndarray:
    result = upper.astype(np.float32) - lower.astype(np.float32)
    return np.clip(result, 0.0, 65535.0).astype(np.float32)
