<template>
  <div class="viewer-wrap" ref="wrap">
    <div
      v-if="imageUrl"
      class="canvas-area"
      @wheel.prevent="onWheel"
      @mousedown="onMouseDown"
      @dblclick.prevent="onDoubleClick"
    >
      <img
        :src="imageUrl"
        class="tif-img"
        draggable="false"
        :style="{
          transform: `translate(${tx}px, ${ty}px) scale(${scale})`,
          transformOrigin: '0 0',
        }"
        @load="onImgLoad"
      />
      <svg
        class="overlay"
        :style="{
          transform: `translate(${tx}px, ${ty}px) scale(${scale})`,
          transformOrigin: '0 0',
          width: `${imgNatW || 1}px`,
          height: `${imgNatH || 1}px`,
        }"
        :viewBox="`0 0 ${imgNatW || 1} ${imgNatH || 1}`"
      >
        <g v-for="ann in annotations" :key="ann.id" :class="{ selected: ann.id === selectedId }">
          <rect
            v-if="ann.type === 'rect'"
            :x="Math.min(ann.x1, ann.x2)"
            :y="Math.min(ann.y1, ann.y2)"
            :width="Math.abs(ann.x2 - ann.x1)"
            :height="Math.abs(ann.y2 - ann.y1)"
            class="shape"
          />
          <ellipse
            v-else-if="ann.type === 'ellipse'"
            :cx="(ann.x1 + ann.x2) / 2"
            :cy="(ann.y1 + ann.y2) / 2"
            :rx="Math.abs(ann.x2 - ann.x1) / 2"
            :ry="Math.abs(ann.y2 - ann.y1) / 2"
            class="shape"
          />
          <polygon
            v-else-if="ann.type === 'polygon'"
            :points="ann.points.map(p => `${p.x},${p.y}`).join(' ')"
            class="shape"
          />
          <polyline
            v-else-if="ann.type === 'brush'"
            :points="ann.points.map(p => `${p.x},${p.y}`).join(' ')"
            class="shape"
          />
        </g>

        <rect
          v-if="draft && draft.type === 'rect'"
          :x="Math.min(draft.x1, draft.x2)"
          :y="Math.min(draft.y1, draft.y2)"
          :width="Math.abs(draft.x2 - draft.x1)"
          :height="Math.abs(draft.y2 - draft.y1)"
          class="shape draft"
        />
        <ellipse
          v-if="draft && draft.type === 'ellipse'"
          :cx="(draft.x1 + draft.x2) / 2"
          :cy="(draft.y1 + draft.y2) / 2"
          :rx="Math.abs(draft.x2 - draft.x1) / 2"
          :ry="Math.abs(draft.y2 - draft.y1) / 2"
          class="shape draft"
        />
        <polygon
          v-if="draft && draft.type === 'polygon'"
          :points="draft.points.map(p => `${p.x},${p.y}`).join(' ')"
          class="shape draft"
        />
        <polyline
          v-if="draft && draft.type === 'brush'"
          :points="draft.points.map(p => `${p.x},${p.y}`).join(' ')"
          class="shape draft"
        />
      </svg>
    </div>
    <div v-else class="placeholder">
      <p>Open a 16-bit TIF file to get started</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  imageUrl: { type: String, default: null },
  mode: { type: String, default: 'select' },
  zoomDelta: { type: Number, default: 0 },
  fitSignal: { type: Number, default: 0 },
})

const wrap = ref(null)
const scale = ref(1)
const tx = ref(0)
const ty = ref(0)
const annotations = ref([])
const selectedId = ref(null)
const draft = ref(null)
let imgNatW = 0, imgNatH = 0
let seq = 0

function onImgLoad(e) {
  imgNatW = e.target.naturalWidth
  imgNatH = e.target.naturalHeight
  annotations.value = []
  selectedId.value = null
  draft.value = null
  fitToScreen()
}

function fitToScreen() {
  if (!wrap.value || !imgNatW) return
  const { clientWidth: cw, clientHeight: ch } = wrap.value
  const s = Math.min(cw / imgNatW, ch / imgNatH, 1)
  scale.value = s
  tx.value = (cw - imgNatW * s) / 2
  ty.value = (ch - imgNatH * s) / 2
}

watch(() => props.fitSignal, fitToScreen)

watch(() => props.zoomDelta, (delta) => {
  if (delta === 0) return
  applyZoom(delta > 0 ? 1.2 : 1 / 1.2, wrap.value
    ? wrap.value.clientWidth / 2
    : 0,
    wrap.value ? wrap.value.clientHeight / 2 : 0)
})

function onWheel(e) {
  const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1
  const rect = wrap.value.getBoundingClientRect()
  applyZoom(factor, e.clientX - rect.left, e.clientY - rect.top)
}

function applyZoom(factor, cx, cy) {
  const newScale = Math.min(Math.max(scale.value * factor, 0.05), 40)
  const ratio = newScale / scale.value
  tx.value = cx - ratio * (cx - tx.value)
  ty.value = cy - ratio * (cy - ty.value)
  scale.value = newScale
}

let dragging = false
let dragMode = null
let lastX = 0, lastY = 0
let dragAnchor = null

function onMouseDown(e) {
  if (e.button !== 0) return
  if (!imgNatW || !imgNatH) return

  const p = toImagePoint(e.clientX, e.clientY)
  if (!p) return

  if (props.mode === 'pan') {
    startPan(e)
    return
  }

  if (props.mode === 'select') {
    const hit = findAnnotationAt(p)
    selectedId.value = hit ? hit.id : null
    if (hit) {
      dragMode = 'move'
      dragAnchor = p
      dragging = true
      window.addEventListener('mousemove', onMouseMove)
      window.addEventListener('mouseup', onMouseUp)
    }
    return
  }

  if (props.mode === 'rect' || props.mode === 'ellipse') {
    draft.value = { id: `d-${++seq}`, type: props.mode, x1: p.x, y1: p.y, x2: p.x, y2: p.y }
    dragMode = 'draw'
    dragging = true
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mouseup', onMouseUp)
    return
  }

  if (props.mode === 'polygon') {
    if (!draft.value || draft.value.type !== 'polygon') {
      draft.value = { id: `d-${++seq}`, type: 'polygon', points: [p] }
    } else {
      const first = draft.value.points[0]
      if (distance(p, first) <= pointTolerance()) {
        commitPolygon()
      } else {
        draft.value.points.push(p)
      }
    }
    return
  }

  if (props.mode === 'brush') {
    draft.value = { id: `d-${++seq}`, type: 'brush', points: [p] }
    dragMode = 'brush'
    dragging = true
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mouseup', onMouseUp)
    return
  }

  if (props.mode === 'erase') {
    eraseAt(p)
    return
  }

  startPan(e)
}

function startPan(e) {
  dragging = true
  dragMode = 'pan'
  lastX = e.clientX
  lastY = e.clientY
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onMouseMove(e) {
  if (!dragging) return
  if (dragMode === 'pan') {
    tx.value += e.clientX - lastX
    ty.value += e.clientY - lastY
    lastX = e.clientX
    lastY = e.clientY
    return
  }

  const p = toImagePoint(e.clientX, e.clientY)
  if (!p) return

  if (dragMode === 'draw' && draft.value) {
    draft.value.x2 = clamp(p.x, 0, imgNatW)
    draft.value.y2 = clamp(p.y, 0, imgNatH)
    return
  }

  if (dragMode === 'brush' && draft.value && draft.value.type === 'brush') {
    draft.value.points.push(clampPoint(p))
    return
  }

  if (dragMode === 'move' && dragAnchor) {
    const ann = annotations.value.find(a => a.id === selectedId.value)
    if (!ann) return
    const dx = p.x - dragAnchor.x
    const dy = p.y - dragAnchor.y
    moveAnnotation(ann, dx, dy)
    dragAnchor = p
    return
  }

  lastX = e.clientX
  lastY = e.clientY
}

function onMouseUp() {
  if (dragMode === 'draw' && draft.value) {
    const w = Math.abs(draft.value.x2 - draft.value.x1)
    const h = Math.abs(draft.value.y2 - draft.value.y1)
    if (w >= 2 && h >= 2) {
      const saved = { ...draft.value, id: `a-${++seq}` }
      annotations.value.push(saved)
      selectedId.value = saved.id
    }
    draft.value = null
  }

  if (dragMode === 'brush' && draft.value && draft.value.points.length > 1) {
    const saved = { ...draft.value, id: `a-${++seq}` }
    annotations.value.push(saved)
    selectedId.value = saved.id
    draft.value = null
  }

  dragging = false
  dragMode = null
  dragAnchor = null
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
}

function onDoubleClick() {
  if (props.mode === 'polygon') commitPolygon()
}

function commitPolygon() {
  if (!draft.value || draft.value.type !== 'polygon') return
  if (draft.value.points.length >= 3) {
    const saved = { ...draft.value, id: `a-${++seq}` }
    annotations.value.push(saved)
    selectedId.value = saved.id
  }
  draft.value = null
}

function toImagePoint(clientX, clientY) {
  if (!wrap.value || scale.value <= 0) return null
  const rect = wrap.value.getBoundingClientRect()
  const x = (clientX - rect.left - tx.value) / scale.value
  const y = (clientY - rect.top - ty.value) / scale.value
  return clampPoint({ x, y })
}

function clampPoint(p) {
  return { x: clamp(p.x, 0, imgNatW), y: clamp(p.y, 0, imgNatH) }
}

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v))
}

function pointTolerance() {
  return Math.max(4, 8 / scale.value)
}

function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y)
}

function findAnnotationAt(p) {
  const tol = pointTolerance()
  for (let i = annotations.value.length - 1; i >= 0; i -= 1) {
    const ann = annotations.value[i]
    if (ann.type === 'rect') {
      const x1 = Math.min(ann.x1, ann.x2)
      const x2 = Math.max(ann.x1, ann.x2)
      const y1 = Math.min(ann.y1, ann.y2)
      const y2 = Math.max(ann.y1, ann.y2)
      if (p.x >= x1 - tol && p.x <= x2 + tol && p.y >= y1 - tol && p.y <= y2 + tol) return ann
    } else if (ann.type === 'ellipse') {
      const cx = (ann.x1 + ann.x2) / 2
      const cy = (ann.y1 + ann.y2) / 2
      const rx = Math.max(Math.abs(ann.x2 - ann.x1) / 2, 1)
      const ry = Math.max(Math.abs(ann.y2 - ann.y1) / 2, 1)
      const nx = (p.x - cx) / rx
      const ny = (p.y - cy) / ry
      if (nx * nx + ny * ny <= 1.05) return ann
    } else if (ann.type === 'polygon' || ann.type === 'brush') {
      if (isNearPolyline(ann.points, p, tol) || isPointInPolygon(p, ann.points)) return ann
    }
  }
  return null
}

function eraseAt(p) {
  const hit = findAnnotationAt(p)
  if (!hit) return
  annotations.value = annotations.value.filter(a => a.id !== hit.id)
  if (selectedId.value === hit.id) selectedId.value = null
}

function moveAnnotation(ann, dx, dy) {
  if (ann.type === 'rect' || ann.type === 'ellipse') {
    ann.x1 = clamp(ann.x1 + dx, 0, imgNatW)
    ann.y1 = clamp(ann.y1 + dy, 0, imgNatH)
    ann.x2 = clamp(ann.x2 + dx, 0, imgNatW)
    ann.y2 = clamp(ann.y2 + dy, 0, imgNatH)
    return
  }
  if (ann.type === 'polygon' || ann.type === 'brush') {
    ann.points = ann.points.map(pt => ({ x: clamp(pt.x + dx, 0, imgNatW), y: clamp(pt.y + dy, 0, imgNatH) }))
  }
}

function isNearPolyline(points, p, tol) {
  if (!points || points.length < 2) return false
  for (let i = 1; i < points.length; i += 1) {
    if (distancePointToSegment(p, points[i - 1], points[i]) <= tol) return true
  }
  return false
}

function distancePointToSegment(p, a, b) {
  const abx = b.x - a.x
  const aby = b.y - a.y
  const apx = p.x - a.x
  const apy = p.y - a.y
  const ab2 = abx * abx + aby * aby
  if (ab2 === 0) return Math.hypot(apx, apy)
  const t = clamp((apx * abx + apy * aby) / ab2, 0, 1)
  const x = a.x + abx * t
  const y = a.y + aby * t
  return Math.hypot(p.x - x, p.y - y)
}

function isPointInPolygon(p, points) {
  if (!points || points.length < 3) return false
  let inside = false
  for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
    const xi = points[i].x
    const yi = points[i].y
    const xj = points[j].x
    const yj = points[j].y
    const intersect = ((yi > p.y) !== (yj > p.y)) &&
      (p.x < ((xj - xi) * (p.y - yi)) / ((yj - yi) || 1e-8) + xi)
    if (intersect) inside = !inside
  }
  return inside
}

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})
</script>

<style scoped>
.viewer-wrap {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #2a2a2a;
  position: relative;
  min-height: 0;
}
.canvas-area {
  width: 100%; height: 100%;
  position: relative;
  cursor: crosshair;
  user-select: none;
}
.tif-img {
  position: absolute;
  top: 0; left: 0;
  image-rendering: pixelated;
  will-change: transform;
}
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}
.shape {
  fill: rgba(30, 144, 255, 0.18);
  stroke: #1e90ff;
  stroke-width: 1.2;
  vector-effect: non-scaling-stroke;
}
.selected .shape {
  stroke: #ff9800;
  fill: rgba(255, 152, 0, 0.15);
}
.draft {
  stroke-dasharray: 4 3;
}
.placeholder {
  display: flex; align-items: center; justify-content: center;
  height: 100%; color: #888; font-size: 16px;
}
</style>
