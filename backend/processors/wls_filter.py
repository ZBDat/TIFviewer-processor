import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve


class Params(BaseModel):
    lambda_value: float = Field(default=1.0, gt=0)
    alpha: float = Field(default=1.2, ge=0.1, le=5.0)
    epsilon: float = Field(default=1e-4, gt=0)
    model_config = ConfigDict(extra="forbid")


def apply(
    image: np.ndarray,
    lambda_value: float = 1.0,
    alpha: float = 1.2,
    epsilon: float = 1e-4,
) -> np.ndarray:
    img = image.astype(np.float32)
    h, w = img.shape
    n = h * w

    log_img = np.log1p(np.clip(img / 65535.0, 0.0, 1.0))
    grad_x = np.diff(log_img, axis=1)
    grad_y = np.diff(log_img, axis=0)

    horizontal_weights = lambda_value / (np.abs(grad_x) ** alpha + epsilon)  # h, w-1
    vertical_weights = lambda_value / (np.abs(grad_y) ** alpha + epsilon)  # h-1, w

    diag = np.ones((h, w), dtype=np.float64)
    diag[:, :-1] += horizontal_weights
    diag[:, 1:] += horizontal_weights
    diag[:-1, :] += vertical_weights
    diag[1:, :] += vertical_weights

    east = np.zeros((h, w), dtype=np.float64)
    west = np.zeros((h, w), dtype=np.float64)
    south = np.zeros((h, w), dtype=np.float64)
    north = np.zeros((h, w), dtype=np.float64)

    east[:, :-1] = -horizontal_weights
    west[:, 1:] = -horizontal_weights
    south[:-1, :] = -vertical_weights
    north[1:, :] = -vertical_weights

    a = diags(
        diagonals=[
            north.reshape(-1),
            west.reshape(-1),
            diag.reshape(-1),
            east.reshape(-1),
            south.reshape(-1),
        ],
        offsets=[-w, -1, 0, 1, w],
        shape=(n, n),
        format="csr",
    )

    out = spsolve(a, img.reshape(-1).astype(np.float64)).reshape(h, w)
    out = np.nan_to_num(out, nan=0.0, posinf=65535.0, neginf=0.0)
    return np.clip(out, 0.0, 65535.0).astype(np.float32)
