<template>
  <div class="param-panel" v-if="selected">
    <div class="param-title">{{ selected.label }}</div>

    <template v-if="selected.type === 'local_contrast_normalization'">
      <SliderRow
        label="Sigma"
        v-model="params.sigma"
        :min="0.30" :max="32.00" :step="0.01"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Epsilon"
        v-model="params.epsilon"
        :min="0.0001" :max="0.50"
        :logarithmic="true"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Output Gain"
        v-model="params.output_gain"
        :min="0.00" :max="4.00" :step="0.01"
        @update:modelValue="emit"
      />
    </template>
    <template v-else>
      <p class="no-params">No parameters</p>
    </template>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import SliderRow from './SliderRow.vue'

const props = defineProps({
  selected: { type: Object, default: null },
})
const emits = defineEmits(['params-changed'])

const params = reactive({ sigma: 25.54, epsilon: 0.08, output_gain: 1.0 })

watch(
  () => props.selected,
  (sel) => {
    if (!sel) return
    if (sel.type === 'local_contrast_normalization') {
      params.sigma = sel.params?.sigma ?? 25.54
      params.epsilon = sel.params?.epsilon ?? 0.08
      params.output_gain = sel.params?.output_gain ?? 1.0
    }
  },
  { immediate: true },
)

watch(params, () => { emit() })

function emit() {
  if (!props.selected) return
  emits('params-changed', { id: props.selected.id, params: { ...params } })
}
</script>

<style scoped>
.param-panel {
  padding: 12px 24px;
  background: #fafafa;
  border-top: 1px solid #e0e0e0;
}
.param-title {
  font-size: 13px; font-weight: 600; margin-bottom: 8px; color: #555;
}
.no-params { font-size: 13px; color: #aaa; }
</style>
