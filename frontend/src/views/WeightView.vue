<script setup lang="ts">
import { ref, onMounted } from 'vue'
import WeightChart from '../components/WeightChart.vue'
import { getWeightHistory, getWeightTrend, logWeight } from '../api/client'
import type { WeightEntry, WeightTrend } from '../types'

const entries = ref<WeightEntry[]>([])
const trendData = ref<WeightTrend[]>([])
const loading = ref(true)

const newWeight = ref('')
const newNotes = ref('')
const submitting = ref(false)

onMounted(load)

async function load() {
  loading.value = true
  try {
    const [e, t] = await Promise.all([
      getWeightHistory(),
      getWeightTrend(365),
    ])
    entries.value = e
    trendData.value = t
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!newWeight.value) return
  submitting.value = true
  try {
    await logWeight({
      weight: parseFloat(newWeight.value),
      notes: newNotes.value || undefined,
    })
    newWeight.value = ''
    newNotes.value = ''
    await load()
  } catch (e) {
    alert('Erreur: ' + (e as Error).message)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">Poids</h1>

    <!-- Quick log -->
    <div class="rounded-2xl p-5 mb-6 shadow-sm"
      :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
      <div class="text-sm font-semibold mb-3">Enregistrer le poids du jour</div>
      <div class="flex gap-2 mb-3">
        <input v-model="newWeight" type="number" step="0.1" placeholder="Poids (kg)"
          class="flex-1 px-4 py-2.5 rounded-xl border outline-none"
          :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }" />
        <button @click="submit" :disabled="submitting || !newWeight"
          class="px-6 py-2.5 rounded-xl font-semibold text-white bg-teal-primary border-0 cursor-pointer disabled:opacity-50">
          {{ submitting ? '...' : 'OK' }}
        </button>
      </div>
      <input v-model="newNotes" placeholder="Notes (optionnel)"
        class="w-full px-4 py-2 rounded-xl border outline-none text-sm"
        :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }" />
    </div>

    <div v-if="loading" class="text-center py-8" :style="{ color: 'var(--text-secondary)' }">Chargement...</div>

    <template v-else>
      <!-- Chart -->
      <div class="rounded-2xl p-4 mb-6 shadow-sm"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="text-sm font-semibold mb-3">Évolution</div>
        <WeightChart :data="trendData" />
      </div>

      <!-- Table -->
      <div class="rounded-2xl shadow-sm overflow-hidden"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="text-sm font-semibold p-4 pb-2">Historique</div>
        <div v-if="entries.length === 0" class="px-4 pb-4 text-sm" :style="{ color: 'var(--text-secondary)' }">
          Aucune entrée
        </div>
        <div v-for="entry in entries" :key="entry.id"
          class="flex justify-between items-center px-4 py-3 border-t"
          :style="{ borderColor: 'var(--border-color)' }">
          <div>
            <div class="text-sm font-medium">{{ new Date(entry.weigh_date).toLocaleDateString('fr-FR') }}</div>
            <div v-if="entry.notes" class="text-xs" :style="{ color: 'var(--text-secondary)' }">{{ entry.notes }}</div>
          </div>
          <div class="text-lg font-bold">{{ entry.weight }} kg</div>
        </div>
      </div>
    </template>
  </div>
</template>
