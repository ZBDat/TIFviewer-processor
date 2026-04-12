<template>
  <div class="node" :class="[kindClass, { active: data.active }]" @click="onClickNode">
    <Handle v-if="kind === 'unary' || kind === 'sink'" type="target" :position="Position.Left" id="in" class="hdl in" :connectable="true" />
    <Handle v-if="kind === 'binary'" type="target" :position="Position.Left" id="in1" class="hdl in hdl-top" :connectable="true" />
    <Handle v-if="kind === 'binary'" type="target" :position="Position.Left" id="in2" class="hdl in hdl-bottom" :connectable="true" />

    <div class="title">{{ data.title }}</div>

    <div v-if="showParams" class="params">
      <label v-for="(v, k) in localParams" :key="k" class="row">
        <span>{{ k }}</span>
        <input
          v-if="typeof v === 'number'"
          type="number"
          :value="v"
          step="any"
          @input="onNum(k, $event)"
        />
        <input
          v-else-if="typeof v === 'boolean'"
          type="checkbox"
          :checked="v"
          @change="onBool(k, $event)"
        />
      </label>
    </div>

    <div v-if="kind === 'sink'" class="view-hint">Click to preview</div>

    <Handle v-if="kind !== 'sink'" type="source" :position="Position.Right" id="out" class="hdl out" :connectable="true" />
  </div>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Handle, Position } from '@vue-flow/core'

const props = defineProps({ data: { type: Object, required: true } })

const localParams = reactive({})

watch(
  () => props.data.params,
  (v) => {
    const next = { ...(v || {}) }
    Object.keys(localParams).forEach((k) => { delete localParams[k] })
    Object.assign(localParams, next)
  },
  { immediate: true, deep: true },
)

const kind = computed(() => props.data.kind || 'unary')
const kindClass = computed(() => `kind-${kind.value}`)
const showParams = computed(() => kind.value !== 'source' && Object.keys(localParams).length > 0)

function onNum(key, e) {
  const parsed = Number(e.target.value)
  localParams[key] = Number.isFinite(parsed) ? parsed : 0
  props.data.onParamsChange?.({ ...localParams })
}

function onBool(key, e) {
  localParams[key] = !!e.target.checked
  props.data.onParamsChange?.({ ...localParams })
}

function onClickNode() {
  if (kind.value === 'sink') {
    props.data.onSelectView?.()
  }
}
</script>

<style scoped>
.node {
  position: relative;
  min-width: 190px;
  max-width: 240px;
  background: #fff;
  border: 1px solid #ced8e2;
  border-radius: 10px;
  padding: 10px;
  box-shadow: 0 6px 18px rgba(10, 24, 39, 0.1);
}

.node.active {
  border-color: #1f6feb;
  box-shadow: 0 0 0 2px rgba(31, 111, 235, 0.22);
}

.title {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 8px;
}

.params {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 11px;
}

.row input[type='number'] {
  width: 92px;
  border: 1px solid #ccd6e1;
  border-radius: 6px;
  padding: 2px 6px;
  font-size: 11px;
}

.view-hint {
  font-size: 11px;
  color: #1f6feb;
  margin-top: 4px;
}

.kind-source {
  border-color: #57a773;
  background: #f1fbf5;
}

.kind-sink {
  border-color: #1f6feb;
  background: #eff6ff;
  cursor: pointer;
}

.kind-binary {
  border-color: #9b6be8;
  background: #f7f2ff;
}

.hdl {
  width: 10px;
  height: 10px;
  border: 2px solid #445;
  background: #fff;
  pointer-events: all;
  z-index: 5;
}

.in {
  left: -7px;
  right: auto;
  top: 50%;
  transform: translateY(-50%);
}

.out {
  right: -7px;
  left: auto;
  top: 50%;
  transform: translateY(-50%);
}

.hdl-top {
  top: 32%;
  transform: translateY(-50%);
}

.hdl-bottom {
  top: 68%;
  transform: translateY(-50%);
}
</style>
