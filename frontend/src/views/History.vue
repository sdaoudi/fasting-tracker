<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import FastCard from '../components/FastCard.vue'
import { getFasts } from '../api/client'
import type { Fast } from '../types'

const fasts = ref<Fast[]>([])
const loading = ref(true)
const filterType = ref('')

const filteredFasts = computed(() => {
  if (!filterType.value) return fasts.value
  return fasts.value.filter(f => f.type === filterType.value)
})

const fastTypes = computed(() => {
  const types = new Set(fasts.value.map(f => f.type))
  return Array.from(types)
})

onMounted(async () => {
  try {
    fasts.value = await getFasts(0, 100)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-4">Historique</h1>

    <!-- Filter -->
    <div v-if="fastTypes.length > 1" class="flex gap-2 mb-4 overflow-x-auto pb-2">
      <button @click="filterType = ''"
        class="px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap border-0 cursor-pointer"
        :class="!filterType ? 'bg-teal-primary text-white' : ''"
        :style="filterType ? { backgroundColor: 'var(--bg-card)', color: 'var(--text-secondary)' } : {}">
        Tous
      </button>
      <button v-for="t in fastTypes" :key="t" @click="filterType = t"
        class="px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap border-0 cursor-pointer"
        :class="filterType === t ? 'bg-teal-primary text-white' : ''"
        :style="filterType !== t ? { backgroundColor: 'var(--bg-card)', color: 'var(--text-secondary)' } : {}">
        {{ t }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-12" :style="{ color: 'var(--text-secondary)' }">Chargement...</div>

    <div v-else-if="filteredFasts.length === 0" class="text-center py-12">
      <div class="text-4xl mb-3">{{'📋'}}</div>
      <div :style="{ color: 'var(--text-secondary)' }">Aucun jeûne enregistré</div>
    </div>

    <div v-else class="flex flex-col gap-3">
      <FastCard v-for="fast in filteredFasts" :key="fast.id" :fast="fast" />
    </div>
  </div>
</template>
