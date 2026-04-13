<template>
  <div class="workflow-overlay" @click.self="$emit('close')">
    <div class="workflow-shell">
      <aside class="palette">
        <div class="palette-title">Enhancements</div>
        <button class="palette-row add-view" @click="addNode('view')">+ View</button>
        <button class="palette-row" @click="duplicateOriginal">+ Duplicate Original</button>
        <div v-for="item in palette" :key="item.type" class="palette-row">
          <span>{{ item.label }}</span>
          <button @click="addNode(item.type)">+</button>
        </div>
      </aside>

      <section class="canvas-wrap">
        <div class="canvas-header">
          <span>Workflow Canvas</span>
          <button class="close-btn" @click="$emit('close')">Done</button>
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
  </div>
</template>

<script setup>
import { markRaw, nextTick, ref, watch } from 'vue'
import { ConnectionMode, VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { WORKFLOW_NODE_TYPES, WORKFLOW_PALETTE } from '../../workflowCatalog'
import WorkflowNodeCard from './WorkflowNodeCard.vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  activeViewId: { type: String, default: null },
})

const emit = defineEmits(['update:modelValue', 'close', 'select-view'])

const nodeTypes = { workflowNode: markRaw(WorkflowNodeCard) }
const palette = WORKFLOW_PALETTE

const flowNodes = ref([])
const flowEdges = ref([])
let seq = 1
let syncingFromProps = false

watch(
  () => props.modelValue,
  (v) => {
    syncingFromProps = true
    const incomingNodes = (v?.nodes || []).map(n => ({ ...n }))
    if (incomingNodes.length === 0) {
      const originalId = `n-${seq++}`
      const viewId = `n-${seq++}`
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
        hydrateNode({
          id: viewId,
          type: 'workflowNode',
          position: { x: 420, y: 120 },
          data: {
            nodeType: 'view',
            title: WORKFLOW_NODE_TYPES.view.label,
            kind: 'sink',
            params: {},
            active: true,
          },
        }),
      ]
      flowEdges.value = [{
        id: `e-${originalId}-${viewId}`,
        source: originalId,
        target: viewId,
        sourceHandle: 'out',
        targetHandle: 'in',
      }]
      emit('select-view', viewId)
      nextTick(() => {
        syncingFromProps = false
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
      active: type === 'view' && id === props.activeViewId,
      onParamsChange: (payload) => onNodeParams(id, payload),
      onSelectView: () => emit('select-view', id),
    },
  }
  flowNodes.value = [...flowNodes.value, hydrateNode(newNode)]
  if (type === 'view') emit('select-view', id)
}

function duplicateOriginal() {
  addNode('original_image')
}

function onNodeParams(nodeId, params) {
  const idx = flowNodes.value.findIndex(n => n.id === nodeId)
  if (idx < 0) return
  const updated = {
    ...flowNodes.value[idx],
    data: {
      ...flowNodes.value[idx].data,
      params: { ...params },
      onParamsChange: (payload) => onNodeParams(nodeId, payload),
      onSelectView: () => emit('select-view', nodeId),
    },
  }
  flowNodes.value = [
    ...flowNodes.value.slice(0, idx),
    hydrateNode(updated),
    ...flowNodes.value.slice(idx + 1),
  ]
}

function onDeleteNode(nodeId) {
  const target = flowNodes.value.find(n => n.id === nodeId)
  if (!target) return
  flowNodes.value = flowNodes.value.filter(n => n.id !== nodeId)
  flowEdges.value = flowEdges.value.filter(e => e.source !== nodeId && e.target !== nodeId)
  if (target.data?.nodeType === 'view' && props.activeViewId === nodeId) {
    selectFallbackView()
  }
}

function hydrateNode(node) {
  const id = node.id
  return {
    ...node,
    data: {
      ...(node.data || {}),
      onParamsChange: (payload) => onNodeParams(id, payload),
      onSelectView: () => emit('select-view', id),
      onDeleteNode: () => onDeleteNode(id),
    },
  }
}

function sanitizeNode(node) {
  const cleanData = { ...(node.data || {}) }
  delete cleanData.onParamsChange
  delete cleanData.onSelectView
  delete cleanData.onDeleteNode
  return {
    ...node,
    data: cleanData,
  }
}

watch(
  () => props.activeViewId,
  (viewId) => {
    flowNodes.value = flowNodes.value.map((n) => ({
      ...n,
      data: {
        ...n.data,
        active: n.data?.nodeType === 'view' && n.id === viewId,
        onParamsChange: (payload) => onNodeParams(n.id, payload),
        onSelectView: () => emit('select-view', n.id),
        onDeleteNode: () => onDeleteNode(n.id),
      },
    }))
  },
  { immediate: true },
)

watch(
  () => flowNodes.value.map(n => n.id),
  () => {
    if (syncingFromProps) return
    ensureActiveViewValid()
  },
)

function onEdgeClick(_event, edge) {
  if (!edge?.id) return
  flowEdges.value = flowEdges.value.filter(e => e.id !== edge.id)
}

function getFallbackViewId() {
  return flowNodes.value.find(n => n.data?.nodeType === 'view')?.id ?? null
}

function selectFallbackView() {
  emit('select-view', getFallbackViewId())
}

function ensureActiveViewValid() {
  const hasActiveView = flowNodes.value.some(
    n => n.data?.nodeType === 'view' && n.id === props.activeViewId,
  )
  if (hasActiveView) return
  selectFallbackView()
}

function onConnect(conn) {
  const source = flowNodes.value.find(n => n.id === conn.source)
  const target = flowNodes.value.find(n => n.id === conn.target)
  if (!source || !target) return

  const sourceKind = source.data?.kind
  const targetKind = target.data?.kind
  if (sourceKind === 'sink') return
  if (targetKind === 'source') return

  if (targetKind === 'unary' || targetKind === 'sink') {
    flowEdges.value = flowEdges.value.filter(e => e.target !== conn.target)
    flowEdges.value = [...flowEdges.value, {
      id: `e-${conn.source}-${conn.target}-${Date.now()}`,
      source: conn.source,
      target: conn.target,
      sourceHandle: 'out',
      targetHandle: 'in',
    }]
    return
  }

  if (targetKind === 'binary') {
    const th = conn.targetHandle || 'in1'
    flowEdges.value = flowEdges.value.filter(e => !(e.target === conn.target && e.targetHandle === th))
    flowEdges.value = [...flowEdges.value, {
      id: `e-${conn.source}-${conn.target}-${th}-${Date.now()}`,
      source: conn.source,
      target: conn.target,
      sourceHandle: 'out',
      targetHandle: th,
    }]
  }
}
</script>

<style scoped>
.workflow-overlay {
  position: fixed;
  inset: 0;
  background: rgba(8, 15, 22, 0.45);
  z-index: 200;
  display: flex;
  align-items: stretch;
  justify-content: center;
}

.workflow-shell {
  width: min(1400px, 96vw);
  margin: 18px 0;
  background: #f6f8fa;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  box-shadow: 0 16px 42px rgba(0, 0, 0, 0.25);
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

.palette-row.add-view,
.palette-row.add-view + .palette-row {
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

.close-btn {
  padding: 6px 10px;
  border-radius: 7px;
  background: #1f6feb;
  color: #fff;
}

.flow {
  flex: 1;
}
</style>
