<template>
  <div class="workflow-shell">
    <aside class="palette">
      <div class="palette-title">Enhancements</div>
      <button class="palette-row" @click="duplicateOriginal">+ Duplicate Original</button>
      <div v-for="item in palette" :key="item.type" class="palette-row">
        <span>{{ item.label }}</span>
        <button @click="addNode(item.type)">+</button>
      </div>
    </aside>

    <section class="canvas-wrap">
      <div class="canvas-header">
        <span>Workflow Canvas</span>
      </div>
      <VueFlow
        v-model:nodes="flowNodes"
        v-model:edges="flowEdges"
        class="flow"
        :node-types="nodeTypes"
        :nodes-draggable="true"
        :nodes-connectable="true"
        :elements-selectable="true"
        :snap-to-grid="true"
        :snap-grid="[20, 20]"
        :connect-on-click="false"
        :connection-mode="ConnectionMode.Loose"
        @connect="onConnect"
        @edge-click="onEdgeClick"
        :fit-view-on-init="true"
      >
        <Background />
        <Controls />
      </VueFlow>
    </section>
  </div>
</template>

<script setup>
import { markRaw, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { ConnectionMode, VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { WORKFLOW_NODE_TYPES, WORKFLOW_PALETTE } from '../../workflowCatalog'
import WorkflowNodeCard from './WorkflowNodeCard.vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  activeNodeId: { type: String, default: null },
})

const emit = defineEmits(['update:modelValue', 'select-node'])

const nodeTypes = { workflowNode: markRaw(WorkflowNodeCard) }
const palette = WORKFLOW_PALETTE

const flowNodes = ref([])
const flowEdges = ref([])
let seq = 1
let syncingFromProps = false
let initializedFromProps = false
const selectedEdgeId = ref(null)

watch(
  () => props.modelValue,
  (v) => {
    if (initializedFromProps) return
    syncingFromProps = true
    const incomingNodes = (v?.nodes || []).map(n => ({ ...n }))
    if (incomingNodes.length === 0) {
      const originalId = `n-${seq++}`
      flowNodes.value = [
        hydrateNode({
          id: originalId,
          type: 'workflowNode',
          position: { x: 120, y: 120 },
          data: {
            nodeType: 'original_image',
            title: WORKFLOW_NODE_TYPES.original_image.label,
            kind: 'source',
            params: {},
          },
        }),
      ]
      flowEdges.value = []
      nextTick(() => {
        syncingFromProps = false
        initializedFromProps = true
      })
      return
    }

    flowNodes.value = incomingNodes.map(n => hydrateNode(n))
    flowEdges.value = (v?.edges || []).map(e => ({ ...e }))
    for (const n of flowNodes.value) {
      const m = /n-(\d+)/.exec(n.id)
      if (m) seq = Math.max(seq, Number(m[1]) + 1)
    }

    nextTick(() => {
      syncingFromProps = false
      initializedFromProps = true
    })
  },
  { immediate: true, deep: true },
)

watch([flowNodes, flowEdges], () => {
  if (syncingFromProps) return
  emit('update:modelValue', {
    nodes: flowNodes.value.map(n => sanitizeNode(n)),
    edges: flowEdges.value.map(e => ({ ...e })),
  })
}, { deep: true })

function addNode(type) {
  const meta = WORKFLOW_NODE_TYPES[type]
  if (!meta) return
  const id = `n-${seq++}`
  const x = 200 + Math.random() * 300
  const y = 80 + Math.random() * 260
  const newNode = {
    id,
    type: 'workflowNode',
    position: { x, y },
    data: {
      nodeType: type,
      title: meta.label,
      kind: meta.kind,
      params: { ...meta.params },
      onParamsChange: (payload) => onNodeParams(id, payload),
      onSelectNode: () => emit('select-node', id),
    },
  }
  flowNodes.value = [...flowNodes.value, hydrateNode(newNode)]
}

function duplicateOriginal() {
  addNode('original_image')
}

function onNodeParams(nodeId, params) {
  const idx = flowNodes.value.findIndex(n => n.id === nodeId)
  if (idx < 0) return
  const node = flowNodes.value[idx]
  flowNodes.value[idx] = hydrateNode({
    ...node,
    data: {
      ...node.data,
      params: { ...params },
      onParamsChange: (payload) => onNodeParams(nodeId, payload),
      onSelectNode: () => emit('select-node', nodeId),
    },
  })
}

function onDeleteNode(nodeId) {
  const target = flowNodes.value.find(n => n.id === nodeId)
  if (!target) return
  flowNodes.value = flowNodes.value.filter(n => n.id !== nodeId)
  flowEdges.value = flowEdges.value.filter(e => e.source !== nodeId && e.target !== nodeId)
  if (selectedEdgeId.value && !flowEdges.value.some(e => e.id === selectedEdgeId.value)) {
    selectedEdgeId.value = null
  }
}

function hydrateNode(node) {
  const id = node.id
  return {
    ...node,
    data: {
      ...(node.data || {}),
      onParamsChange: (payload) => onNodeParams(id, payload),
      onDeleteNode: () => onDeleteNode(id),
      onSelectNode: () => emit('select-node', id),
      active: id === props.activeNodeId,
    },
  }
}

function sanitizeNode(node) {
  const cleanData = { ...(node.data || {}) }
  delete cleanData.onParamsChange
  delete cleanData.onDeleteNode
  delete cleanData.onSelectNode
  return {
    ...node,
    data: cleanData,
  }
}

watch(
  () => props.activeNodeId,
  (activeId) => {
    flowNodes.value = flowNodes.value.map((n) => ({
      ...n,
      data: {
        ...n.data,
        active: n.id === activeId,
        onParamsChange: (payload) => onNodeParams(n.id, payload),
        onDeleteNode: () => onDeleteNode(n.id),
        onSelectNode: () => emit('select-node', n.id),
      },
    }))
  },
  { immediate: true },
)

watch(
  () => flowEdges.value.map(e => e.id),
  (ids) => {
    if (selectedEdgeId.value && !ids.includes(selectedEdgeId.value)) {
      selectedEdgeId.value = null
    }
  },
)

function onEdgeClick(_event, edge) {
  if (!edge?.id) return
  selectedEdgeId.value = edge.id
}

function onKeydown(e) {
  if (e.key !== 'Delete' && e.key !== 'Backspace') return
  if (!selectedEdgeId.value) return
  flowEdges.value = flowEdges.value.filter(edge => edge.id !== selectedEdgeId.value)
  selectedEdgeId.value = null
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})

function onConnect(conn) {
  const source = flowNodes.value.find(n => n.id === conn.source)
  const target = flowNodes.value.find(n => n.id === conn.target)
  if (!source || !target) return

  const targetKind = target.data?.kind
  if (targetKind === 'source') return

  if (targetKind === 'unary') {
    flowEdges.value = flowEdges.value.filter(e => e.target !== conn.target)
    const newEdge = {
      id: `e-${conn.source}-${conn.target}-${Date.now()}`,
      source: conn.source,
      target: conn.target,
      sourceHandle: 'out',
      targetHandle: 'in',
    }
    flowEdges.value = [...flowEdges.value, newEdge]
    selectedEdgeId.value = newEdge.id
    return
  }

  if (targetKind === 'binary') {
    const th = conn.targetHandle || 'in1'
    flowEdges.value = flowEdges.value.filter(e => !(e.target === conn.target && e.targetHandle === th))
    const newEdge = {
      id: `e-${conn.source}-${conn.target}-${th}-${Date.now()}`,
      source: conn.source,
      target: conn.target,
      sourceHandle: 'out',
      targetHandle: th,
    }
    flowEdges.value = [...flowEdges.value, newEdge]
    selectedEdgeId.value = newEdge.id
  }
}
</script>

<style scoped>
.workflow-shell {
  width: 100%;
  height: 100%;
  background: #f6f8fa;
  overflow: hidden;
  display: flex;
}

.palette {
  width: 280px;
  padding: 12px;
  border-right: 1px solid #d9e0e8;
  background: #f2f5f8;
  overflow-y: auto;
}

.palette-title {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 10px;
}

.palette-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #d2dae3;
  border-radius: 8px;
  padding: 6px 8px;
  margin-bottom: 8px;
  background: #fff;
  font-size: 12px;
}

.palette-row button {
  width: 24px;
  height: 24px;
  border-radius: 5px;
  background: #0f7a5a;
  color: #fff;
}

.palette-row:first-of-type {
  width: 100%;
  justify-content: center;
  background: #ebf7f2;
  border-color: #b9dfd2;
  color: #1c6b55;
  font-weight: 600;
}

.canvas-wrap {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.canvas-header {
  height: 44px;
  border-bottom: 1px solid #d9e0e8;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  font-size: 13px;
  font-weight: 700;
}

.flow {
  flex: 1;
}
</style>
