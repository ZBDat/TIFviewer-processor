import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class Params(BaseModel):
    epsilon: float = Field(default=1e-6, gt=0)
    model_config = ConfigDict(extra="forbid")


def apply(upper: np.ndarray, lower: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
    result = upper.astype(np.float32) / (lower.astype(np.float32) + float(epsilon))
    max_val = float(np.max(result))
    if max_val > 0:
        result = result / max_val * 65535.0
    return np.clip(result, 0.0, 65535.0).astype(np.float32)
