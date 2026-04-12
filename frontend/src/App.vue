<template>
  <div class="app">
    <aside class="sidebar">
      <Histogram :histogram="histogram" />
      <button class="workflow-btn" @click="openWorkflowEditor">Open Enhancement Workflow</button>
      <div class="workflow-tip">
        Click a <code>View</code> node in the workflow canvas to preview that branch.
      </div>
    </aside>

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
          :mode="toolMode"
          :zoomDelta="zoomDelta"
          :fitSignal="fitSignal"
        />
        <div v-if="loading" class="loading-overlay">Processing…</div>
      </div>
    </main>

    <input ref="fileInput" type="file" accept=".tif,.tiff" style="display:none" @change="onFileInputChange" />

    <WorkflowEditor
      v-if="workflowOpen"
      v-model="workflow"
      :activeViewId="activeViewId"
      @close="workflowOpen = false"
      @select-view="onSelectView"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import Histogram from './components/Histogram.vue'
import Toolbar from './components/Toolbar.vue'
import ImageViewer from './components/ImageViewer.vue'
import WorkflowEditor from './components/workflow/WorkflowEditor.vue'
import { WORKFLOW_NODE_TYPES } from './workflowCatalog'

const fileInput = ref(null)
const fileId = ref(null)
const imageUrl = ref(null)
const histogram = ref(null)
const toolMode = ref('select')
const loading = ref(false)
const zoomDelta = ref(0)
const fitSignal = ref(0)
const workflowOpen = ref(false)
const activeViewId = ref(null)
const workflow = ref({ nodes: [], edges: [] })

let latestProcessRequestId = 0
let processAbortController = null

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
    ensureWorkflowInit()
    await refreshWorkflowResult()
  } catch (err) {
    alert('Upload failed: ' + err.message)
  } finally {
    loading.value = false
  }
}

function ensureWorkflowInit() {
  if (workflow.value.nodes.length > 0) return

  const original = {
    id: 'n-1',
    type: 'workflowNode',
    position: { x: 120, y: 120 },
    data: {
      nodeType: 'original_image',
      title: WORKFLOW_NODE_TYPES.original_image.label,
      kind: 'source',
      params: {},
    },
  }
  const view = {
    id: 'n-2',
    type: 'workflowNode',
    position: { x: 420, y: 120 },
    data: {
      nodeType: 'view',
      title: WORKFLOW_NODE_TYPES.view.label,
      kind: 'sink',
      params: {},
      active: true,
    },
  }
  const edge = {
    id: 'e-n-1-n-2',
    source: 'n-1',
    target: 'n-2',
    sourceHandle: 'out',
    targetHandle: 'in',
  }
  workflow.value = { nodes: [original, view], edges: [edge] }
  activeViewId.value = view.id
}

function openWorkflowEditor() {
  ensureWorkflowInit()
  workflowOpen.value = true
}

function onSelectView(viewId) {
  activeViewId.value = viewId
  refreshWorkflowResult()
}

watch(workflow, () => {
  refreshWorkflowResult()
}, { deep: true })

function toGraphPayload() {
  const nodes = (workflow.value.nodes || []).map((n) => ({
    id: n.id,
    type: n.data?.nodeType,
    params: { ...(n.data?.params || {}) },
  }))
  const edges = (workflow.value.edges || []).map((e) => ({
    source: e.source,
    target: e.target,
    source_handle: e.sourceHandle || 'out',
    target_handle: e.targetHandle || 'in',
  }))
  return { nodes, edges }
}

async function refreshWorkflowResult() {
  if (!fileId.value) return
  if (!activeViewId.value) return
  const requestId = ++latestProcessRequestId
  if (processAbortController) {
    processAbortController.abort()
  }
  processAbortController = new AbortController()

  loading.value = true
  try {
    const graph = toGraphPayload()
    const payload = { file_id: fileId.value, nodes: graph.nodes, edges: graph.edges, view_id: activeViewId.value }
    const res = await fetch('/api/process-graph', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: processAbortController.signal,
    })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    if (requestId !== latestProcessRequestId) return

    imageUrl.value = `data:image/png;base64,${data.image}`
    histogram.value = data.histogram
  } catch (err) {
    if (err.name === 'AbortError') return
    console.error('Process error:', err)
  } finally {
    if (requestId === latestProcessRequestId) {
      loading.value = false
    }
  }
}

function onZoom(delta) {
  zoomDelta.value = delta
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
  background: #eef3f8;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  overflow-y: auto;
}

.workflow-btn {
  border-radius: 8px;
  padding: 10px 12px;
  background: #0f7a5a;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
}

.workflow-tip {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #d5dde7;
  padding: 10px;
  font-size: 12px;
  color: #445;
  line-height: 1.4;
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
