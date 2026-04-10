import io
import json
import uuid
import base64
from typing import Any, Optional

import numpy as np
import tifffile
from PIL import Image
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from processors import PROCESSORS

app = FastAPI(title="TIF Viewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store: file_id -> numpy array (float32, range 0-65535).
# Replace with a persistent cache (e.g. Redis / disk) for production use.
image_store: dict[str, np.ndarray] = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _apply_pipeline(image: np.ndarray, enhancements: list[dict]) -> np.ndarray:
    """Apply a list of {type, params} dicts sequentially."""
    result = image.copy()
    for enh in enhancements:
        enh_type = enh.get("type")
        params = enh.get("params") or {}
        processor = PROCESSORS.get(enh_type)
        if processor is None:
            raise HTTPException(status_code=400, detail=f"Unknown enhancement: {enh_type!r}")
        result = processor(result, **params)
    return result


def _to_png_bytes(
    image: np.ndarray,
    min_val: Optional[float],
    max_val: Optional[float],
) -> bytes:
    """Normalise to 8-bit and encode as PNG."""
    img = image.astype(np.float32)
    lo = float(min_val) if min_val is not None else float(img.min())
    hi = float(max_val) if max_val is not None else float(img.max())
    if hi == lo:
        hi = lo + 1.0
    img_8 = ((img - lo) / (hi - lo) * 255.0).clip(0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(img_8, mode="L").save(buf, format="PNG")
    return buf.getvalue()


def _compute_histogram(image: np.ndarray) -> dict:
    """256-bin histogram over [0, 65535]."""
    counts, edges = np.histogram(image, bins=256, range=(0, 65535))
    bins = ((edges[:-1] + edges[1:]) / 2.0).astype(int).tolist()
    return {"bins": bins, "counts": counts.tolist()}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "message": "TIF Viewer API"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".tif", ".tiff")):
        raise HTTPException(status_code=400, detail="Only .tif / .tiff files are accepted")

    data = await file.read()
    try:
        img = tifffile.imread(io.BytesIO(data))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read TIFF: {exc}")

    # Flatten to 2-D grayscale
    if img.ndim == 3:
        img = img[..., 0] if img.shape[2] == 1 else img.mean(axis=2)
    elif img.ndim != 2:
        raise HTTPException(status_code=400, detail="Unsupported TIFF dimensionality")

    img = img.astype(np.float32)

    file_id = str(uuid.uuid4())
    image_store[file_id] = img
    return {"file_id": file_id, "width": int(img.shape[1]), "height": int(img.shape[0])}


@app.get("/api/image/{file_id}")
def get_image(
    file_id: str,
    enhancements: Optional[str] = None,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
):
    if file_id not in image_store:
        raise HTTPException(status_code=404, detail="File not found")

    img = image_store[file_id]

    if enhancements:
        try:
            enh_list = json.loads(enhancements)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid enhancements JSON")
        img = _apply_pipeline(img, enh_list)

    return Response(content=_to_png_bytes(img, min_val, max_val), media_type="image/png")


@app.get("/api/histogram/{file_id}")
def get_histogram(file_id: str):
    if file_id not in image_store:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(_compute_histogram(image_store[file_id]))


class ProcessRequest(BaseModel):
    file_id: str
    enhancements: list[dict[str, Any]] = []
    min_val: Optional[float] = None
    max_val: Optional[float] = None


@app.post("/api/process")
def process_image(req: ProcessRequest):
    if req.file_id not in image_store:
        raise HTTPException(status_code=404, detail="File not found")

    img = _apply_pipeline(image_store[req.file_id], req.enhancements)
    b64 = base64.b64encode(_to_png_bytes(img, req.min_val, req.max_val)).decode()
    return {"image": b64, "histogram": _compute_histogram(img)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
