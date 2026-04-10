<template>
  <div class="toolbar">
    <!-- File open -->
    <input ref="fileInput" type="file" accept=".tif,.tiff" style="display:none" @change="onFileChange" />
    <button title="Open file" @click="$refs.fileInput.click()">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"/>
      </svg>
    </button>

    <div class="sep"/>

    <!-- Annotation tools (placeholders) -->
    <button title="Select" :class="{active: mode==='select'}" @click="$emit('mode','select')">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M5 3l14 9-7 1-4 7z"/>
      </svg>
    </button>
    <button title="Pan" :class="{active: mode==='pan'}" @click="$emit('mode','pan')">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M5 9V5h4M19 9V5h-4M5 15v4h4M19 15v4h-4"/>
      </svg>
    </button>
    <button title="Rectangle" :class="{active: mode==='rect'}" @click="$emit('mode','rect')">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="5" width="18" height="14" rx="1"/>
      </svg>
    </button>
    <button title="Ellipse" :class="{active: mode==='ellipse'}" @click="$emit('mode','ellipse')">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <ellipse cx="12" cy="12" rx="9" ry="6"/>
      </svg>
    </button>
    <button title="Polygon" :class="{active: mode==='polygon'}" @click="$emit('mode','polygon')">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="12,3 21,9 17,20 7,20 3,9"/>
      </svg>
    </button>
    <button title="Brush" :class="{active: mode==='brush'}" @click="$emit('mode','brush')">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M9.06 11.9l8.07-8.06a2.85 2.85 0 114.03 4.03l-8.06 8.07L9.06 11.9z"/>
        <path d="M7 16a2 2 0 100 4 2 2 0 000-4z"/>
      </svg>
    </button>
    <button title="Erase" :class="{active: mode==='erase'}" @click="$emit('mode','erase')">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 20H7L3 16l11-11 6 6-4 4"/>
      </svg>
    </button>

    <div class="sep"/>

    <!-- Zoom controls -->
    <button title="Zoom out" @click="$emit('zoom',-1)">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        <line x1="8" y1="11" x2="14" y2="11"/>
      </svg>
    </button>
    <button title="Zoom in" @click="$emit('zoom',1)">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        <line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
      </svg>
    </button>
    <button title="Fit to screen" @click="$emit('fit')">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/>
        <line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
defineProps({ mode: { type: String, default: 'select' } })
const emit = defineEmits(['mode', 'zoom', 'fit', 'open-file'])

function onFileChange(e) {
  const f = e.target.files[0]
  if (f) emit('open-file', f)
  e.target.value = ''
}
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
}
.toolbar button {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 4px;
  color: #555;
  transition: background 0.15s;
}
.toolbar button:hover { background: #f0f0f0; opacity: 1; }
.toolbar button.active { background: #e3effe; color: #1a73e8; }
.sep { width: 1px; height: 20px; background: #ddd; margin: 0 4px; }
</style>
