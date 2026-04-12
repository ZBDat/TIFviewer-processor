# TIFviewer-processor

A frontend-backend separated tool for viewing and processing **16-bit grayscale TIFF** images.

## Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Backend  | Python · FastAPI · tifffile · NumPy · scikit-image · scipy |
| Frontend | Vue 3 · Vite · Chart.js · vuedraggable  |

## Features

* Upload 16-bit TIF/TIFF files
* Grayscale histogram with hover tooltip (Value / Distribution)
* Composable enhancement pipeline (drag-to-reorder, add/remove)
  * Histogram Equalization
  * Local Contrast Normalization (Sigma, Epsilon, Output Gain sliders)
* Image viewer with scroll-to-zoom and drag-to-pan
* Toolbar with zoom in/out/fit and annotation-mode placeholders

## Quick start

### Unified startup

```bash
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
python start.py
```

This starts both backend and frontend together and automatically opens
**http://localhost:5173** in your browser.

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py          # starts on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev             # starts on http://localhost:5173
```

Open **http://localhost:5173** in your browser. The Vite dev-server proxies
all `/api/*` requests to the FastAPI backend automatically.

## API reference

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/upload` | Upload a `.tif`/`.tiff` file; returns `file_id` |
| `GET`  | `/api/image/{file_id}` | Render processed PNG (query: `enhancements`, `min_val`, `max_val`) |
| `GET`  | `/api/histogram/{file_id}` | 256-bin histogram JSON |
| `POST` | `/api/process` | Apply pipeline; returns base64 PNG + histogram |

## Project layout

```
backend/
  main.py                 FastAPI application
  requirements.txt
  processors/
    histogram_eq.py       Histogram equalization
    local_contrast_norm.py  Local contrast normalization
frontend/
  src/
    App.vue               Root component / layout
    components/
      Histogram.vue       Chart.js histogram panel
      EnhancementPanel.vue  Pipeline list (drag-and-drop)
      ParameterPanel.vue  Slider controls
      SliderRow.vue       Single slider with value display
      ImageViewer.vue     Pan / zoom image display
      Toolbar.vue         File open + zoom + annotation toolbar
  vite.config.js          Proxies /api → localhost:8000
```
