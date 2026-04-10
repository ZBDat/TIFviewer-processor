<template>
  <div class="hist-wrap">
    <div class="hist-title">Gray</div>
    <div class="chart-container">
      <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
      <div v-else class="no-data">—</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
} from 'chart.js'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip)

const props = defineProps({
  histogram: { type: Object, default: null }, // { bins: [], counts: [] }
})

const chartData = computed(() => {
  if (!props.histogram) return null
  return {
    labels: props.histogram.bins,
    datasets: [
      {
        data: props.histogram.counts,
        backgroundColor: 'rgba(100,100,100,0.7)',
        borderWidth: 0,
        barPercentage: 1.0,
        categoryPercentage: 1.0,
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title: (items) => `Value ${items[0].label}`,
        label: (item) => `Distribution ${item.raw}`,
      },
    },
  },
  scales: {
    x: {
      ticks: {
        maxTicksLimit: 6,
        callback(val, idx) {
          // show value in ×10^4
          return (this.getLabelForValue(val) / 10000).toFixed(1)
        },
        font: { size: 10 },
      },
      title: {
        display: true,
        text: '×10⁴',
        font: { size: 10 },
        align: 'end',
      },
      grid: { display: false },
    },
    y: {
      ticks: {
        maxTicksLimit: 5,
        callback(val) {
          return val >= 10000 ? (val / 10000).toFixed(1) : val
        },
        font: { size: 10 },
      },
      title: {
        display: true,
        text: '×10⁴',
        font: { size: 10 },
        align: 'end',
      },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
  },
}
</script>

<style scoped>
.hist-wrap {
  padding: 8px 8px 4px;
  background: #fff;
  border-radius: 6px;
  margin-bottom: 8px;
}
.hist-title {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  text-align: center;
}
.chart-container {
  height: 200px;
  position: relative;
}
.no-data {
  display: flex; align-items: center; justify-content: center;
  height: 100%; color: #bbb; font-size: 20px;
}
</style>
