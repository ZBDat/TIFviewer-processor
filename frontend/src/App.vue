<template>
  <div class="app">
    <section class="workflow-pane">
      <WorkflowEditor v-model="workflow" :activeNodeId="activeNodeId" @select-node="onSelectNode" />
    </section>

    <section class="viewer-pane">
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
    </section>

    <div class="hist-floating">
      <Histogram :histogram="histogram" />
    </div>

    <input ref="fileInput" type="file" accept=".tif,.tiff" style="display:none" @change="onFileInputChange" />
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
const workflow = ref({ nodes: [], edges: [] })
const activeNodeId = ref(null)

let latestProcessRequestId = 0
let processAbortController = null

const UPLOAD_TIMEOUT_MS = 30000
const PROCESS_TIMEOUT_MS = 30000

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
  const uploadController = new AbortController()
  let uploadTimedOut = false
  const uploadTimeoutId = setTimeout(() => {
    uploadTimedOut = true
    uploadController.abort()
  }, UPLOAD_TIMEOUT_MS)

  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: fd,
      signal: uploadController.signal,
    })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    fileId.value = data.file_id
    ensureWorkflowInit()
    activeNodeId.value = workflow.value.nodes[0]?.id ?? null
    await refreshActiveNodeResult()
  } catch (err) {
    if (err.name === 'AbortError' && uploadTimedOut) {
      alert('Upload timeout: server processing took too long.')
      return
    }
    alert('Upload failed: ' + err.message)
  } finally {
    clearTimeout(uploadTimeoutId)
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
  workflow.value = { nodes: [original], edges: [] }
}

function onSelectNode(nodeId) {
  activeNodeId.value = nodeId
  refreshActiveNodeResult()
}

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

watch(workflow, () => {
  if (!activeNodeId.value) return
  const exists = (workflow.value.nodes || []).some((n) => n.id === activeNodeId.value)
  if (!exists) {
    activeNodeId.value = workflow.value.nodes[0]?.id ?? null
  }
  if (activeNodeId.value) {
    refreshActiveNodeResult()
  }
}, { deep: true })

async function refreshActiveNodeResult() {
  if (!fileId.value) return
  if (!activeNodeId.value) return
  const requestId = ++latestProcessRequestId
  if (processAbortController) {
    processAbortController.abort()
  }
  processAbortController = new AbortController()
  const controller = processAbortController
  let processTimedOut = false
  const processTimeoutId = setTimeout(() => {
    processTimedOut = true
    controller.abort()
  }, PROCESS_TIMEOUT_MS)

  loading.value = true
  try {
    const graph = toGraphPayload()
    const payload = {
      file_id: fileId.value,
      nodes: graph.nodes,
      edges: graph.edges,
      target_id: activeNodeId.value,
    }
    const res = await fetch('/api/process-graph', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    if (requestId !== latestProcessRequestId) return

    imageUrl.value = `data:image/png;base64,${data.image}`
    histogram.value = data.histogram
  } catch (err) {
    if (err.name === 'AbortError') {
      if (processTimedOut) {
        alert('Processing timeout: image workflow took too long.')
      }
      return
    }
    console.error('Process error:', err)
  } finally {
    clearTimeout(processTimeoutId)
    if (processAbortController === controller) {
      processAbortController = null
    }
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
  position: relative;
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #e9eef3;
}

.viewer-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  border-left: 1px solid #d3dbe5;
}

.workflow-pane {
  width: 48%;
  min-width: 560px;
  background: #f6f8fa;
}

.viewer-container {
  flex: 1;
  position: relative;
  min-height: 0;
}

.hist-floating {
  position: absolute;
  right: 14px;
  top: 14px;
  width: 320px;
  z-index: 120;
  box-shadow: 0 10px 24px rgba(15, 28, 45, 0.24);
  border-radius: 8px;
  overflow: hidden;
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
