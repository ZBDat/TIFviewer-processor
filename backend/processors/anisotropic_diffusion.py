import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class Params(BaseModel):
    iterations: int = Field(default=10, ge=1, le=100)
    kappa: float = Field(default=30.0, gt=0)
    gamma: float = Field(default=0.15, gt=0, le=0.25)
    model_config = ConfigDict(extra="forbid")


def apply(
    image: np.ndarray,
    iterations: int = 10,
    kappa: float = 30.0,
    gamma: float = 0.15,
) -> np.ndarray:
    img = image.astype(np.float32).copy()

    for _ in range(iterations):
        delta_n = np.zeros_like(img)
        delta_s = np.zeros_like(img)
        delta_e = np.zeros_like(img)
        delta_w = np.zeros_like(img)

        delta_n[:-1, :] = img[1:, :] - img[:-1, :]
        delta_s[1:, :] = img[:-1, :] - img[1:, :]
        delta_e[:, :-1] = img[:, 1:] - img[:, :-1]
        delta_w[:, 1:] = img[:, :-1] - img[:, 1:]

        c_n = np.exp(-(delta_n / kappa) ** 2)
        c_s = np.exp(-(delta_s / kappa) ** 2)
        c_e = np.exp(-(delta_e / kappa) ** 2)
        c_w = np.exp(-(delta_w / kappa) ** 2)

        img += gamma * (
            c_n * delta_n +
            c_s * delta_s +
            c_e * delta_e +
            c_w * delta_w
        )

    return np.clip(img, 0.0, 65535.0).astype(np.float32)
