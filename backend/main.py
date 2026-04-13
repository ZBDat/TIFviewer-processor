import io
import json
import uuid
import base64
import threading
from dataclasses import dataclass
from collections import OrderedDict
from typing import Any, Callable, Optional

import numpy as np
import tifffile
from PIL import Image
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from processors import PROCESSOR_SPECS

app = FastAPI(title="TIF Viewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGE_CACHE_LIMIT_BYTES = 2 * 1024 * 1024 * 1024


class ImageCache:
    def __init__(self, max_bytes: int):
        self.max_bytes = max_bytes
        self._items: OrderedDict[str, np.ndarray] = OrderedDict()
        self._used_bytes = 0
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[np.ndarray]:
        with self._lock:
            value = self._items.get(key)
            if value is None:
                return None
            self._items.move_to_end(key)
            return value

    def put(self, key: str, image: np.ndarray) -> bool:
        image_bytes = int(image.nbytes)
        if image_bytes > self.max_bytes:
            return False

        with self._lock:
            prev = self._items.pop(key, None)
            if prev is not None:
                self._used_bytes -= int(prev.nbytes)

            while self._used_bytes + image_bytes > self.max_bytes and self._items:
                _, evicted = self._items.popitem(last=False)
                self._used_bytes -= int(evicted.nbytes)

            if self._used_bytes + image_bytes > self.max_bytes:
                return False

            self._items[key] = image
            self._used_bytes += image_bytes
            return True


image_store = ImageCache(max_bytes=IMAGE_CACHE_LIMIT_BYTES)


class EnhancementRequest(BaseModel):
    type: str
    params: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid")


enhancement_list_adapter = TypeAdapter(list[EnhancementRequest])


@dataclass(frozen=True)
class ValidatedEnhancement:
    type: str
    apply: Callable[..., np.ndarray]
    params: dict[str, Any]
    kind: str


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_request, _exc):
    return JSONResponse(status_code=422, content={"detail": "invalid request"})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_enhancements(raw_items: list[EnhancementRequest]) -> list[ValidatedEnhancement]:
    validated: list[ValidatedEnhancement] = []
    for item in raw_items:
        spec = PROCESSOR_SPECS.get(item.type)
        if spec is None:
            raise HTTPException(status_code=400, detail="invalid enhancement parameters")

        try:
            params = spec.params_model.model_validate(item.params).model_dump()
        except ValidationError:
            raise HTTPException(status_code=400, detail="invalid enhancement parameters")

        validated.append(
            ValidatedEnhancement(
                type=item.type,
                apply=spec.apply,
                params=params,
                kind=spec.kind,
            )
        )

    return validated


def _apply_pipeline(image: np.ndarray, enhancements: list[ValidatedEnhancement]) -> np.ndarray:
    """Apply unary pipeline with optional binary operations between two steps."""
    result = image.copy()
    i = 0

    while i < len(enhancements):
        enh = enhancements[i]
        if enh.kind != "unary":
            raise HTTPException(status_code=400, detail="invalid enhancement parameters")

        input_image = result
        try:
            upper_result = enh.apply(input_image, **enh.params)
        except Exception:
            raise HTTPException(status_code=400, detail="invalid enhancement parameters")

        if i + 1 < len(enhancements) and enhancements[i + 1].kind == "binary":
            if i + 2 >= len(enhancements):
                raise HTTPException(status_code=400, detail="invalid enhancement parameters")

            op = enhancements[i + 1]
            lower_step = enhancements[i + 2]
            if lower_step.kind != "unary":
                raise HTTPException(status_code=400, detail="invalid enhancement parameters")

            try:
                lower_result = lower_step.apply(input_image, **lower_step.params)
                result = op.apply(upper_result, lower_result, **op.params)
            except Exception:
                raise HTTPException(status_code=400, detail="invalid enhancement parameters")

            i += 3
            continue

        result = upper_result
        i += 1

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
    filename = (file.filename or "").lower()
    if not filename.endswith((".tif", ".tiff")):
        raise HTTPException(status_code=400, detail="Only .tif / .tiff files are accepted")

    try:
        file.file.seek(0)
        img = tifffile.imread(file.file)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid image format")

    if img.ndim != 2:
        raise HTTPException(status_code=422, detail="invalid image format")
    if img.dtype.kind != "u" or img.dtype.itemsize != 2:
        raise HTTPException(status_code=422, detail="invalid image format")

    img = img.astype(np.uint16, copy=False)

    if int(img.nbytes) > IMAGE_CACHE_LIMIT_BYTES:
        raise HTTPException(status_code=413, detail="image too large")

    file_id = str(uuid.uuid4())
    if not image_store.put(file_id, img):
        raise HTTPException(status_code=503, detail="server cache is full")

    return {"file_id": file_id, "width": int(img.shape[1]), "height": int(img.shape[0])}


@app.get("/api/image/{file_id}")
def get_image(
    file_id: str,
    enhancements: Optional[str] = None,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
):
    img = image_store.get(file_id)
    if img is None:
        raise HTTPException(status_code=404, detail="File not found")

    if enhancements:
        try:
            parsed = json.loads(enhancements)
            raw_items = enhancement_list_adapter.validate_python(parsed)
        except (json.JSONDecodeError, ValidationError):
            raise HTTPException(status_code=400, detail="invalid enhancement parameters")
        enh_list = _validate_enhancements(raw_items)
        img = _apply_pipeline(img, enh_list)

    return Response(content=_to_png_bytes(img, min_val, max_val), media_type="image/png")


@app.get("/api/histogram/{file_id}")
def get_histogram(file_id: str):
    img = image_store.get(file_id)
    if img is None:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(_compute_histogram(img))


class ProcessRequest(BaseModel):
    file_id: str
    enhancements: list[EnhancementRequest] = Field(default_factory=list)
    min_val: Optional[float] = None
    max_val: Optional[float] = None


class GraphNodeRequest(BaseModel):
    id: str
    type: str
    params: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid")


class GraphEdgeRequest(BaseModel):
    source: str
    source_handle: str = Field(default="out")
    target: str
    target_handle: str = Field(default="in")
    model_config = ConfigDict(extra="forbid")


class ProcessGraphRequest(BaseModel):
    file_id: str
    nodes: list[GraphNodeRequest]
    edges: list[GraphEdgeRequest] = Field(default_factory=list)
    target_id: Optional[str] = None
    view_id: Optional[str] = None


@app.post("/api/process")
def process_image(req: ProcessRequest):
    src = image_store.get(req.file_id)
    if src is None:
        raise HTTPException(status_code=404, detail="File not found")

    img = _apply_pipeline(src, _validate_enhancements(req.enhancements))
    b64 = base64.b64encode(_to_png_bytes(img, req.min_val, req.max_val)).decode()
    return {"image": b64, "histogram": _compute_histogram(img)}


@app.post("/api/process-graph")
def process_graph(req: ProcessGraphRequest):
    src = image_store.get(req.file_id)
    if src is None:
        raise HTTPException(status_code=404, detail="File not found")

    node_map: dict[str, GraphNodeRequest] = {n.id: n for n in req.nodes}
    target_id = req.target_id or req.view_id
    if not target_id or target_id not in node_map:
        raise HTTPException(status_code=400, detail="invalid enhancement parameters")

    incoming: dict[str, list[GraphEdgeRequest]] = {node_id: [] for node_id in node_map}
    for edge in req.edges:
        if edge.source not in node_map or edge.target not in node_map:
            raise HTTPException(status_code=400, detail="invalid enhancement parameters")
        incoming[edge.target].append(edge)

    cache: dict[str, np.ndarray] = {}
    visiting: set[str] = set()

    def eval_node(node_id: str) -> np.ndarray:
        if node_id in cache:
            return cache[node_id]
        if node_id in visiting:
            raise HTTPException(status_code=400, detail="invalid enhancement parameters")

        visiting.add(node_id)
        node = node_map[node_id]
        node_type = node.type

        if node_type == "original_image":
            out = src.astype(np.float32)
        elif node_type == "view":
            inputs = incoming.get(node_id, [])
            if len(inputs) != 1:
                raise HTTPException(status_code=400, detail="invalid enhancement parameters")
            out = eval_node(inputs[0].source)
        else:
            spec = PROCESSOR_SPECS.get(node_type)
            if spec is None:
                raise HTTPException(status_code=400, detail="invalid enhancement parameters")

            try:
                params = spec.params_model.model_validate(node.params).model_dump()
            except ValidationError:
                raise HTTPException(status_code=400, detail="invalid enhancement parameters")

            inputs = incoming.get(node_id, [])

            if spec.kind == "unary":
                if len(inputs) != 1:
                    raise HTTPException(status_code=400, detail="invalid enhancement parameters")
                in_img = eval_node(inputs[0].source)
                try:
                    out = spec.apply(in_img, **params)
                except Exception:
                    raise HTTPException(status_code=400, detail="invalid enhancement parameters")
            else:
                if len(inputs) != 2:
                    raise HTTPException(status_code=400, detail="invalid enhancement parameters")

                upper_edge = next((e for e in inputs if e.target_handle == "in1"), None)
                lower_edge = next((e for e in inputs if e.target_handle == "in2"), None)
                if upper_edge is None or lower_edge is None:
                    raise HTTPException(status_code=400, detail="invalid enhancement parameters")

                upper = eval_node(upper_edge.source)
                lower = eval_node(lower_edge.source)
                try:
                    out = spec.apply(upper, lower, **params)
                except Exception:
                    raise HTTPException(status_code=400, detail="invalid enhancement parameters")

        visiting.remove(node_id)
        cache[node_id] = out.astype(np.float32)
        return cache[node_id]

    img = eval_node(target_id)
    b64 = base64.b64encode(_to_png_bytes(img, None, None)).decode()
    return {"image": b64, "histogram": _compute_histogram(img)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
