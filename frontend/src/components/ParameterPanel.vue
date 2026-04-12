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
    <template v-else-if="selected.type === 'gamma_correction'">
      <SliderRow
        label="Gamma"
        v-model="params.gamma"
        :min="0.10" :max="5.00" :step="0.01"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Gain"
        v-model="params.gain"
        :min="0.10" :max="4.00" :step="0.01"
        @update:modelValue="emit"
      />
    </template>
    <template v-else-if="selected.type === 'log_correction'">
      <SliderRow
        label="Gain"
        v-model="params.gain"
        :min="0.10" :max="4.00" :step="0.01"
        @update:modelValue="emit"
      />
      <label class="toggle-row">
        <span>Inverse</span>
        <input type="checkbox" v-model="params.inv" @change="emit" />
      </label>
    </template>
    <template v-else-if="selected.type === 'sigmoid_correction'">
      <SliderRow
        label="Cutoff"
        v-model="params.cutoff"
        :min="0.00" :max="1.00" :step="0.01"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Gain"
        v-model="params.gain"
        :min="0.10" :max="40.00" :step="0.10"
        @update:modelValue="emit"
      />
      <label class="toggle-row">
        <span>Inverse</span>
        <input type="checkbox" v-model="params.inv" @change="emit" />
      </label>
    </template>
    <template v-else-if="selected.type === 'tophat' || selected.type === 'white_tophat'">
      <SliderRow
        label="Size"
        v-model="params.size"
        :min="1" :max="127" :step="1"
        @update:modelValue="emit"
      />
    </template>
    <template v-else-if="selected.type === 'gaussian_blur'">
      <SliderRow
        label="Sigma"
        v-model="params.sigma"
        :min="0.10" :max="20.00" :step="0.10"
        @update:modelValue="emit"
      />
    </template>
    <template v-else-if="selected.type === 'median_blur'">
      <SliderRow
        label="Size"
        v-model="params.size"
        :min="1" :max="31" :step="1"
        @update:modelValue="emit"
      />
    </template>
    <template v-else-if="selected.type === 'rescale_intensity'">
      <SliderRow
        label="In Low"
        v-model="params.in_low"
        :min="0" :max="65535" :step="1"
        @update:modelValue="emit"
      />
      <SliderRow
        label="In High"
        v-model="params.in_high"
        :min="0" :max="65535" :step="1"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Out Low"
        v-model="params.out_low"
        :min="0" :max="65535" :step="1"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Out High"
        v-model="params.out_high"
        :min="0" :max="65535" :step="1"
        @update:modelValue="emit"
      />
    </template>
    <template v-else-if="selected.type === 'divide_operation'">
      <SliderRow
        label="Epsilon"
        v-model="params.epsilon"
        :min="0.000001" :max="0.01" :step="0.000001"
        :logarithmic="true"
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

const params = reactive({
  sigma: 25.54,
  epsilon: 0.08,
  output_gain: 1.0,
  gamma: 1.0,
  gain: 1.0,
  inv: false,
  cutoff: 0.5,
  size: 15,
  in_low: 0,
  in_high: 65535,
  out_low: 0,
  out_high: 65535,
  epsilon: 0.000001,
})

watch(
  () => props.selected,
  (sel) => {
    if (!sel) return
    if (sel.type === 'local_contrast_normalization') {
      params.sigma = sel.params?.sigma ?? 25.54
      params.epsilon = sel.params?.epsilon ?? 0.08
      params.output_gain = sel.params?.output_gain ?? 1.0
    } else if (sel.type === 'gamma_correction') {
      params.gamma = sel.params?.gamma ?? 1.0
      params.gain = sel.params?.gain ?? 1.0
    } else if (sel.type === 'log_correction') {
      params.gain = sel.params?.gain ?? 1.0
      params.inv = !!(sel.params?.inv ?? false)
    } else if (sel.type === 'sigmoid_correction') {
      params.cutoff = sel.params?.cutoff ?? 0.5
      params.gain = sel.params?.gain ?? 10.0
      params.inv = !!(sel.params?.inv ?? false)
    } else if (sel.type === 'tophat' || sel.type === 'white_tophat') {
      params.size = sel.params?.size ?? 15
    } else if (sel.type === 'gaussian_blur') {
      params.sigma = sel.params?.sigma ?? 1.5
    } else if (sel.type === 'median_blur') {
      params.size = sel.params?.size ?? 3
    } else if (sel.type === 'rescale_intensity') {
      params.in_low = sel.params?.in_low ?? 0
      params.in_high = sel.params?.in_high ?? 65535
      params.out_low = sel.params?.out_low ?? 0
      params.out_high = sel.params?.out_high ?? 65535
    } else if (sel.type === 'divide_operation') {
      params.epsilon = sel.params?.epsilon ?? 0.000001
    }
  },
  { immediate: true },
)

watch(params, () => { emit() })

function emit() {
  if (!props.selected) return
  let payload = {}
  switch (props.selected.type) {
    case 'local_contrast_normalization':
      payload = {
        sigma: params.sigma,
        epsilon: params.epsilon,
        output_gain: params.output_gain,
      }
      break
    case 'gamma_correction':
      payload = { gamma: params.gamma, gain: params.gain }
      break
    case 'log_correction':
      payload = { gain: params.gain, inv: params.inv }
      break
    case 'sigmoid_correction':
      payload = { cutoff: params.cutoff, gain: params.gain, inv: params.inv }
      break
    case 'tophat':
    case 'white_tophat':
      payload = { size: Math.round(params.size) }
      break
    case 'gaussian_blur':
      payload = { sigma: params.sigma }
      break
    case 'median_blur':
      payload = { size: Math.max(1, Math.round(params.size)) }
      break
    case 'rescale_intensity':
      payload = {
        in_low: Math.round(params.in_low),
        in_high: Math.round(params.in_high),
        out_low: Math.round(params.out_low),
        out_high: Math.round(params.out_high),
      }
      break
    case 'divide_operation':
      payload = { epsilon: params.epsilon }
      break
    default:
      payload = {}
  }
  emits('params-changed', { id: props.selected.id, params: payload })
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
.toggle-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #555;
  margin: 6px 0;
}
</style>
