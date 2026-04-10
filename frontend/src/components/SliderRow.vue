<template>
  <div class="slider-row">
    <label class="label">{{ label }}</label>
    <span class="min-label">Min: {{ formatVal(min) }}</span>
    <div class="track">
      <input
        type="range"
        :min="sliderMin"
        :max="sliderMax"
        :step="sliderStep"
        :value="sliderVal"
        @input="onInput"
      />
      <div class="cur-label" :style="{ left: pct + '%' }">{{ formatVal(modelValue) }}</div>
    </div>
    <span class="max-label">Max: {{ formatVal(max) }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  modelValue: Number,
  min: Number,
  max: Number,
  step: Number,
  logarithmic: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

// For epsilon we use log scale
const sliderMin = computed(() => props.logarithmic ? 0 : props.min)
const sliderMax = computed(() => props.logarithmic ? 1 : props.max)
const sliderStep = computed(() => props.logarithmic ? 0.001 : (props.step ?? 0.01))

const sliderVal = computed(() => {
  if (props.logarithmic) {
    const lo = Math.log10(props.min)
    const hi = Math.log10(props.max)
    return (Math.log10(props.modelValue) - lo) / (hi - lo)
  }
  return props.modelValue
})

const pct = computed(() => {
  const lo = sliderMin.value
  const hi = sliderMax.value
  return ((sliderVal.value - lo) / (hi - lo)) * 100
})

function onInput(e) {
  let v = parseFloat(e.target.value)
  if (props.logarithmic) {
    const lo = Math.log10(props.min)
    const hi = Math.log10(props.max)
    v = Math.pow(10, lo + v * (hi - lo))
  }
  emit('update:modelValue', parseFloat(v.toFixed(4)))
}

function formatVal(v) {
  if (v === undefined || v === null) return ''
  if (v < 0.01) return v.toExponential(0)
  if (v >= 10) return v.toFixed(2)
  return v.toFixed(2)
}
</script>

<style scoped>
.slider-row {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; padding: 4px 0;
}
.label { width: 90px; text-align: right; color: #555; }
.min-label, .max-label { white-space: nowrap; color: #777; font-size: 12px; min-width: 62px; }
.max-label { text-align: left; }
.track {
  flex: 1; position: relative; padding-top: 18px;
}
.track input[type=range] { width: 100%; }
.cur-label {
  position: absolute; top: 0;
  transform: translateX(-50%);
  font-size: 11px; color: #333; white-space: nowrap;
  pointer-events: none;
}
</style>
