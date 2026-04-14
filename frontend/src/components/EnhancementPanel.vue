<template>
  <div class="enh-panel">
    <div class="enh-header">
      <span>Enhancement</span>
      <div class="add-wrap">
        <button class="add-btn" @click="toggleMenu" title="Add enhancement">+</button>
        <div v-if="menuOpen" class="add-menu">
          <div
            v-for="opt in OPTIONS"
            :key="opt.type"
            class="add-item"
            @click="addEnhancement(opt)"
          >{{ opt.label }}</div>
        </div>
      </div>
    </div>

    <draggable
      v-model="localList"
      item-key="id"
      handle=".drag-handle"
      @end="emitList"
      class="enh-list"
    >
      <template #item="{ element, index }">
        <div
          class="enh-item"
          :class="{ selected: selectedId === element.id }"
          @click="$emit('select', element)"
        >
          <span class="idx">{{ index + 1 }}</span>
          <span class="name">{{ element.label }}</span>
          <span class="drag-handle">⠿</span>
          <button class="remove-btn" @click.stop="remove(element.id)">×</button>
        </div>
      </template>
    </draggable>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import draggable from 'vuedraggable'

const OPTIONS = [
  { type: 'histogram_equalization', label: 'Histogram Equalization', params: {} },
  {
    type: 'local_contrast_normalization',
    label: 'Local Contrast Normalization',
    params: { sigma: 25.54, epsilon: 0.08, output_gain: 1.0 },
  },
  {
    type: 'gamma_correction',
    label: 'Gamma Correction',
    params: { gamma: 1.0, gain: 1.0 },
  },
  {
    type: 'log_correction',
    label: 'Log Correction',
    params: { gain: 1.0, inv: false },
  },
  {
    type: 'sigmoid_correction',
    label: 'Sigmoid Correction',
    params: { cutoff: 0.5, gain: 10.0, inv: false },
  },
  {
    type: 'tophat',
    label: 'Tophat',
    params: { size: 15 },
  },
  {
    type: 'white_tophat',
    label: 'White-Tophat',
    params: { size: 15 },
  },
  {
    type: 'gaussian_blur',
    label: 'Gaussian Blur',
    params: { sigma: 1.5 },
  },
  {
    type: 'median_blur',
    label: 'Median Blur',
    params: { size: 3 },
  },
  {
    type: 'homomorphic_filter',
    label: 'Homomorphic Filter',
    params: { sigma: 10.0, low_gain: 0.5, high_gain: 1.5 },
  },
  {
    type: 'wls_filter',
    label: 'WLS Filter',
    params: { lambda_value: 1.0, alpha: 1.2, epsilon: 0.0001 },
  },
  {
    type: 'anisotropic_diffusion',
    label: 'Anisotropic Diffusion',
    params: { iterations: 10, kappa: 30.0, gamma: 0.15 },
  },
  {
    type: 'guided_filter',
    label: 'Guided Filter',
    params: { radius: 8, epsilon: 0.01 },
  },
  {
    type: 'rescale_intensity',
    label: 'Rescale Intensity',
    params: { in_low: 0, in_high: 65535, out_low: 0, out_high: 65535 },
  },
  {
    type: 'add_operation',
    label: 'Add (Upper + Lower)',
    params: {},
  },
  {
    type: 'subtract_operation',
    label: 'Subtract (Upper - Lower)',
    params: {},
  },
  {
    type: 'divide_operation',
    label: 'Divide (Upper / Lower)',
    params: { epsilon: 0.000001 },
  },
]

const props = defineProps({
  enhancements: { type: Array, default: () => [] },
  selectedId: { type: String, default: null },
})
const emit = defineEmits(['update:enhancements', 'select'])

let nextId = 1
const localList = ref(props.enhancements.map(e => ({ ...e })))
const menuOpen = ref(false)

watch(() => props.enhancements, (v) => { localList.value = v.map(e => ({ ...e })) }, { deep: true })

function toggleMenu() { menuOpen.value = !menuOpen.value }

function addEnhancement(opt) {
  const item = { id: `enh-${nextId++}`, type: opt.type, label: opt.label, params: { ...opt.params } }
  localList.value = [...localList.value, item]
  menuOpen.value = false
  emitList()
  emit('select', item)
}

function remove(id) {
  localList.value = localList.value.filter(e => e.id !== id)
  emitList()
}

function emitList() {
  emit('update:enhancements', localList.value.map(e => ({ ...e })))
}
</script>

<style scoped>
.enh-panel {
  background: #fff;
  border-radius: 6px;
  padding: 8px;
}
.enh-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 8px;
}
.add-wrap { position: relative; }
.add-btn {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: #e0e0e0;
  font-size: 18px;
  line-height: 1;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.add-btn:hover { background: #ccc; opacity: 1; }
.add-menu {
  position: absolute; right: 0; top: 28px;
  background: #fff; border: 1px solid #ddd;
  border-radius: 4px; z-index: 100;
  min-width: 220px; box-shadow: 0 2px 8px rgba(0,0,0,.15);
}
.add-item {
  padding: 8px 12px; font-size: 13px; cursor: pointer;
}
.add-item:hover { background: #f5f5f5; }
.enh-list { display: flex; flex-direction: column; gap: 4px; }
.enh-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  border: 1px solid transparent;
  transition: background 0.1s;
}
.enh-item:hover { background: #f0f4ff; }
.enh-item.selected { background: #e3effe; border-color: #93bff8; font-weight: 600; }
.idx { color: #888; width: 14px; flex-shrink: 0; }
.name { flex: 1; }
.drag-handle { color: #bbb; cursor: grab; font-size: 16px; }
.remove-btn { color: #aaa; font-size: 16px; line-height: 1; }
.remove-btn:hover { color: #e55; opacity: 1; }
</style>
