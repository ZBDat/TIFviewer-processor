<template>
  <div class="viewer-wrap" ref="wrap">
    <div
      v-if="imageUrl"
      class="canvas-area"
      @wheel.prevent="onWheel"
      @mousedown="onMouseDown"
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
  zoomDelta: { type: Number, default: 0 },
  fitSignal: { type: Number, default: 0 },
})

const wrap = ref(null)
const scale = ref(1)
const tx = ref(0)
const ty = ref(0)
let imgNatW = 0, imgNatH = 0

function onImgLoad(e) {
  imgNatW = e.target.naturalWidth
  imgNatH = e.target.naturalHeight
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

// Pan
let dragging = false, lastX = 0, lastY = 0

function onMouseDown(e) {
  if (e.button !== 0) return
  dragging = true
  lastX = e.clientX
  lastY = e.clientY
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onMouseMove(e) {
  if (!dragging) return
  tx.value += e.clientX - lastX
  ty.value += e.clientY - lastY
  lastX = e.clientX
  lastY = e.clientY
}

function onMouseUp() {
  dragging = false
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
}

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})
</script>

<style scoped>
.viewer-wrap {
  flex: 1;
  overflow: hidden;
  background: #2a2a2a;
  position: relative;
  min-height: 0;
}
.canvas-area {
  width: 100%; height: 100%;
  position: relative;
  cursor: grab;
  user-select: none;
}
.canvas-area:active { cursor: grabbing; }
.tif-img {
  position: absolute;
  top: 0; left: 0;
  image-rendering: pixelated;
  will-change: transform;
}
.placeholder {
  display: flex; align-items: center; justify-content: center;
  height: 100%; color: #888; font-size: 16px;
}
</style>
