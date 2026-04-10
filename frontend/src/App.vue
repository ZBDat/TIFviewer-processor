<template>
  <div class="app">
    <!-- Left sidebar -->
    <aside class="sidebar">
      <Histogram :histogram="histogram" />
      <EnhancementPanel
        v-model:enhancements="enhancements"
        :selectedId="selectedEnhancement?.id"
        @select="onSelectEnhancement"
      />
    </aside>

    <!-- Main area -->
    <main class="main">
      <Toolbar
        @open-file="onFileSelected"
        :mode="toolMode"
        @mode="toolMode = $event"
        @zoom="onZoom"
        @fit="fitSignal++"
      />
      <div class="viewer-container">
        <ImageViewer
          :imageUrl="imageUrl"
          :zoomDelta="zoomDelta"
          :fitSignal="fitSignal"
        />
        <div v-if="loading" class="loading-overlay">Processing…</div>
      </div>
      <ParameterPanel :selected="selectedEnhancement" @params-changed="onParamsChanged" />
    </main>

    <!-- Hidden file input -->
    <input ref="fileInput" type="file" accept=".tif,.tiff" style="display:none" @change="onFileInputChange" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import Histogram from './components/Histogram.vue'
import EnhancementPanel from './components/EnhancementPanel.vue'
import Toolbar from './components/Toolbar.vue'
import ImageViewer from './components/ImageViewer.vue'
import ParameterPanel from './components/ParameterPanel.vue'

const fileInput = ref(null)
const fileId = ref(null)
const imageUrl = ref(null)
const histogram = ref(null)
const enhancements = ref([])
const selectedEnhancement = ref(null)
const toolMode = ref('select')
const loading = ref(false)
const zoomDelta = ref(0)
const fitSignal = ref(0)

let debounceTimer = null

// ── File upload ───────────────────────────────────────────────────────────────
function onFileSelected(file) {
  if (file) uploadFile(file)
}

function onFileInputChange(e) {
  const f = e.target.files[0]
  if (f) uploadFile(f)
  e.target.value = ''
}

async function uploadFile(file) {
  loading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch('/api/upload', { method: 'POST', body: fd })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    fileId.value = data.file_id
    enhancements.value = []
    selectedEnhancement.value = null
    await refreshAll()
  } catch (err) {
    alert('Upload failed: ' + err.message)
  } finally {
    loading.value = false
  }
}

// ── Enhancement pipeline ──────────────────────────────────────────────────────
function onSelectEnhancement(enh) {
  selectedEnhancement.value = enh
}

watch(enhancements, () => { scheduleProcess() }, { deep: true })

function onParamsChanged({ id, params }) {
  const idx = enhancements.value.findIndex(e => e.id === id)
  if (idx !== -1) {
    enhancements.value[idx] = { ...enhancements.value[idx], params }
    if (selectedEnhancement.value?.id === id) {
      selectedEnhancement.value = { ...enhancements.value[idx] }
    }
  }
  scheduleProcess()
}

function scheduleProcess() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(refreshAll, 300)
}

// ── API calls ─────────────────────────────────────────────────────────────────
async function refreshAll() {
  if (!fileId.value) return
  loading.value = true
  try {
    const payload = {
      file_id: fileId.value,
      enhancements: enhancements.value.map(e => ({ type: e.type, params: e.params || {} })),
    }
    const res = await fetch('/api/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    imageUrl.value = `data:image/png;base64,${data.image}`
    histogram.value = data.histogram
  } catch (err) {
    console.error('Process error:', err)
  } finally {
    loading.value = false
  }
}

// ── Zoom / toolbar ────────────────────────────────────────────────────────────
function onZoom(delta) {
  zoomDelta.value = delta
  // reset so next same-direction click still triggers
  setTimeout(() => { zoomDelta.value = 0 }, 50)
}
</script>

<style scoped>
.app {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ── Left sidebar ─────────────────────────── */
.sidebar {
  width: 360px;
  flex-shrink: 0;
  background: #f0f0f0;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  overflow-y: auto;
}

/* ── Main content ─────────────────────────── */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.viewer-container {
  flex: 1;
  position: relative;
  min-height: 0;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.35);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  z-index: 50;
  pointer-events: none;
}
</style>
