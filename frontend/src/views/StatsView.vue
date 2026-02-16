<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip } from 'chart.js'
import StatCard from '../components/StatCard.vue'
import WeightChart from '../components/WeightChart.vue'
import { getStats, getWeightTrend } from '../api/client'
import type { Stats, WeightTrend } from '../types'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip)

const stats = ref<Stats | null>(null)
const weightData = ref<WeightTrend[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [s, w] = await Promise.all([
      getStats(),
      getWeightTrend(365),
    ])
    stats.value = s
    weightData.value = w
  } finally {
    loading.value = false
  }
})

const byTypeChart = computed(() => {
  if (!stats.value) return null
  const labels = Object.keys(stats.value.by_type)
  const data = Object.values(stats.value.by_type)
  return {
    data: {
      labels,
      datasets: [{
        label: 'Jeunes',
        data,
        backgroundColor: '#0d9488',
        borderRadius: 8,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, ticks: { stepSize: 1 } },
      },
    },
  }
})
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">Statistiques</h1>

    <div v-if="loading" class="text-center py-12" :style="{ color: 'var(--text-secondary)' }">Chargement...</div>

    <template v-else-if="stats">
      <div class="grid grid-cols-2 gap-3 mb-6">
        <StatCard icon="⏱️" label="Jeunes total" :value="stats.total_fasts" />
        <StatCard icon="✅" label="Completes" :value="stats.completed_fasts" />
        <StatCard icon="📏" label="Duree moyenne" :value="stats.avg_duration_hours ? stats.avg_duration_hours + 'h' : '-'" />
        <StatCard icon="⚖️" label="Poids perdu" :value="stats.total_weight_lost ? stats.total_weight_lost.toFixed(1) + ' kg' : '-'" />
      </div>

      <!-- By type chart -->
      <div v-if="byTypeChart && Object.keys(stats.by_type).length > 0" class="rounded-2xl p-4 shadow-sm mb-6"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="text-sm font-semibold mb-3">Jeunes par type</div>
        <div style="height: 200px;">
          <Bar :data="byTypeChart.data" :options="byTypeChart.options" />
        </div>
      </div>

      <!-- Weight chart -->
      <div class="rounded-2xl p-4 shadow-sm mb-6"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="text-sm font-semibold mb-3">Evolution du poids</div>
        <WeightChart :data="weightData" />
      </div>
    </template>
  </div>
</template>
