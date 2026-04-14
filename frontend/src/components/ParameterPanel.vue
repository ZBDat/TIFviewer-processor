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
    <template v-else-if="selected.type === 'homomorphic_filter'">
      <SliderRow
        label="Sigma"
        v-model="params.hf_sigma"
        :min="1.00" :max="128.00" :step="0.10"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Low Gain"
        v-model="params.hf_low_gain"
        :min="0.00" :max="1.00" :step="0.01"
        @update:modelValue="emit"
      />
      <SliderRow
        label="High Gain"
        v-model="params.hf_high_gain"
        :min="1.00" :max="5.00" :step="0.01"
        @update:modelValue="emit"
      />
    </template>
    <template v-else-if="selected.type === 'wls_filter'">
      <SliderRow
        label="Lambda"
        v-model="params.wls_lambda"
        :min="0.01" :max="10.00" :step="0.01"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Alpha"
        v-model="params.wls_alpha"
        :min="0.10" :max="5.00" :step="0.01"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Epsilon"
        v-model="params.wls_epsilon"
        :min="0.000001" :max="0.01"
        :logarithmic="true"
        @update:modelValue="emit"
      />
    </template>
    <template v-else-if="selected.type === 'anisotropic_diffusion'">
      <SliderRow
        label="Iterations"
        v-model="params.ad_iterations"
        :min="1" :max="100" :step="1"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Kappa"
        v-model="params.ad_kappa"
        :min="1.00" :max="100.00" :step="0.10"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Gamma"
        v-model="params.ad_gamma"
        :min="0.01" :max="0.25" :step="0.01"
        @update:modelValue="emit"
      />
    </template>
    <template v-else-if="selected.type === 'guided_filter'">
      <SliderRow
        label="Radius"
        v-model="params.gf_radius"
        :min="1" :max="128" :step="1"
        @update:modelValue="emit"
      />
      <SliderRow
        label="Epsilon"
        v-model="params.gf_epsilon"
        :min="0.000001" :max="0.1"
        :logarithmic="true"
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
  hf_sigma: 10.0,
  hf_low_gain: 0.5,
  hf_high_gain: 1.5,
  wls_lambda: 1.0,
  wls_alpha: 1.2,
  wls_epsilon: 0.0001,
  ad_iterations: 10,
  ad_kappa: 30.0,
  ad_gamma: 0.15,
  gf_radius: 8,
  gf_epsilon: 0.01,
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
    } else if (sel.type === 'homomorphic_filter') {
      params.hf_sigma = sel.params?.sigma ?? 10.0
      params.hf_low_gain = sel.params?.low_gain ?? 0.5
      params.hf_high_gain = sel.params?.high_gain ?? 1.5
    } else if (sel.type === 'wls_filter') {
      params.wls_lambda = sel.params?.lambda_value ?? 1.0
      params.wls_alpha = sel.params?.alpha ?? 1.2
      params.wls_epsilon = sel.params?.epsilon ?? 0.0001
    } else if (sel.type === 'anisotropic_diffusion') {
      params.ad_iterations = sel.params?.iterations ?? 10
      params.ad_kappa = sel.params?.kappa ?? 30.0
      params.ad_gamma = sel.params?.gamma ?? 0.15
    } else if (sel.type === 'guided_filter') {
      params.gf_radius = sel.params?.radius ?? 8
      params.gf_epsilon = sel.params?.epsilon ?? 0.01
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
    case 'homomorphic_filter':
      payload = {
        sigma: params.hf_sigma,
        low_gain: params.hf_low_gain,
        high_gain: params.hf_high_gain,
      }
      break
    case 'wls_filter':
      payload = {
        lambda_value: params.wls_lambda,
        alpha: params.wls_alpha,
        epsilon: params.wls_epsilon,
      }
      break
    case 'anisotropic_diffusion':
      payload = {
        iterations: Math.max(1, Math.round(params.ad_iterations)),
        kappa: params.ad_kappa,
        gamma: params.ad_gamma,
      }
      break
    case 'guided_filter':
      payload = {
        radius: Math.max(1, Math.round(params.gf_radius)),
        epsilon: params.gf_epsilon,
      }
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
