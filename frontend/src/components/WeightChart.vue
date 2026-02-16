<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Filler
} from 'chart.js'
import type { WeightTrend } from '../types'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler)

const props = defineProps<{
  data: WeightTrend[]
  mini?: boolean
}>()

const chartData = computed(() => ({
  labels: props.data.map(d => {
    const dt = new Date(d.weigh_date)
    return dt.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
  }),
  datasets: [{
    label: 'Poids (kg)',
    data: props.data.map(d => d.weight),
    borderColor: '#0d9488',
    backgroundColor: 'rgba(13, 148, 136, 0.1)',
    fill: true,
    tension: 0.3,
    pointRadius: props.mini ? 0 : 3,
    pointBackgroundColor: '#0d9488',
  }],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: !props.mini },
  },
  scales: {
    x: { display: !props.mini, grid: { display: false } },
    y: {
      display: !props.mini,
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
  },
}))
</script>

<template>
  <div :style="{ height: mini ? '80px' : '250px' }">
    <Line v-if="data.length > 0" :data="chartData" :options="chartOptions" />
    <div v-else class="flex items-center justify-center h-full text-sm" :style="{ color: 'var(--text-secondary)' }">
      Aucune donnee de poids
    </div>
  </div>
</template>
