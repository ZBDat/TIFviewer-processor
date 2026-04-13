export const WORKFLOW_NODE_TYPES = {
  original_image: {
    label: 'Original Image',
    kind: 'source',
    params: {},
  },
  histogram_equalization: {
    label: 'Histogram Equalization',
    kind: 'unary',
    params: {},
  },
  local_contrast_normalization: {
    label: 'Local Contrast Normalization',
    kind: 'unary',
    params: { sigma: 25.54, epsilon: 0.08, output_gain: 1.0 },
  },
  gamma_correction: {
    label: 'Gamma Correction',
    kind: 'unary',
    params: { gamma: 1.0, gain: 1.0 },
  },
  log_correction: {
    label: 'Log Correction',
    kind: 'unary',
    params: { gain: 1.0, inv: false },
  },
  sigmoid_correction: {
    label: 'Sigmoid Correction',
    kind: 'unary',
    params: { cutoff: 0.5, gain: 10.0, inv: false },
  },
  tophat: {
    label: 'Tophat',
    kind: 'unary',
    params: { size: 15 },
  },
  white_tophat: {
    label: 'White-Tophat',
    kind: 'unary',
    params: { size: 15 },
  },
  gaussian_blur: {
    label: 'Gaussian Blur',
    kind: 'unary',
    params: { sigma: 1.5 },
  },
  median_blur: {
    label: 'Median Blur',
    kind: 'unary',
    params: { size: 3 },
  },
  rescale_intensity: {
    label: 'Rescale Intensity',
    kind: 'unary',
    params: { in_low: 0, in_high: 65535, out_low: 0, out_high: 65535 },
  },
  add_operation: {
    label: 'Add',
    kind: 'binary',
    params: {},
  },
  subtract_operation: {
    label: 'Subtract',
    kind: 'binary',
    params: {},
  },
  divide_operation: {
    label: 'Divide',
    kind: 'binary',
    params: { epsilon: 0.000001 },
  },
}

export const WORKFLOW_PALETTE = Object.entries(WORKFLOW_NODE_TYPES)
  .filter(([type]) => type !== 'original_image')
  .map(([type, meta]) => ({
    type,
    label: meta.label,
    kind: meta.kind,
    params: { ...meta.params },
  }))
