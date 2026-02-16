<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import MealRecommendationCard from './MealRecommendationCard.vue'
import MealDetailModal from './MealDetailModal.vue'
import type { MealRecommendation } from '../types'
import {
  useMealRecommendations,
  CATEGORY_LABELS,
  TIMING_LABELS,
} from '../composables/useMealRecommendations'

const props = defineProps<{
  fastId?: number | null
  fastDuration?: string | null
  compact?: boolean
}>()

const { recommendations, loading, error, fetchSuggestions } = useMealRecommendations()

const selectedRec = ref<MealRecommendation | null>(null)
const activeCategory = ref<string | null>(null)
const activeTiming = ref<string | null>(null)

const categoryOptions = ['rupture_jeune', 'repas_fenetre', 'reprise_progressive']
const timingOptions = ['petit_dejeuner', 'dejeuner', 'diner', 'collation']

async function loadRecommendations() {
  await fetchSuggestions({
    fast_id: props.fastId ?? undefined,
    fast_duration: props.fastDuration ?? undefined,
    meal_timing: activeTiming.value ?? undefined,
    limit: props.compact ? 3 : 100,
  })
}

onMounted(loadRecommendations)

watch([activeCategory, activeTiming], () => {
  loadRecommendations()
})

const filteredRecommendations = computed(() => {
  let results = recommendations.value
  if (activeCategory.value) {
    results = results.filter(r => r.category === activeCategory.value)
  }
  return results
})

function onSelect(rec: MealRecommendation) {
  selectedRec.value = rec
}

function onLogged() {
  setTimeout(() => { selectedRec.value = null }, 1200)
}
</script>

<template>
  <div>
    <!-- Filters (hidden in compact mode) -->
    <div v-if="!compact" class="mb-4">
      <!-- Category filter -->
      <div class="flex gap-2 overflow-x-auto pb-2 mb-2 -mx-1 px-1">
        <button
          class="shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors"
          :class="!activeCategory ? 'text-white' : ''"
          :style="{
            backgroundColor: !activeCategory ? 'var(--color-teal-primary)' : 'var(--bg-primary)',
            color: !activeCategory ? 'white' : 'var(--text-secondary)',
          }"
          @click="activeCategory = null"
        >
          Tout
        </button>
        <button
          v-for="cat in categoryOptions"
          :key="cat"
          class="shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors"
          :style="{
            backgroundColor: activeCategory === cat ? 'var(--color-teal-primary)' : 'var(--bg-primary)',
            color: activeCategory === cat ? 'white' : 'var(--text-secondary)',
          }"
          @click="activeCategory = activeCategory === cat ? null : cat"
        >
          {{ CATEGORY_LABELS[cat] || cat }}
        </button>
      </div>

      <!-- Timing filter -->
      <div class="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
        <button
          class="shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors"
          :style="{
            backgroundColor: !activeTiming ? 'var(--color-teal-primary)' : 'var(--bg-primary)',
            color: !activeTiming ? 'white' : 'var(--text-secondary)',
          }"
          @click="activeTiming = null"
        >
          Tous moments
        </button>
        <button
          v-for="t in timingOptions"
          :key="t"
          class="shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors"
          :style="{
            backgroundColor: activeTiming === t ? 'var(--color-teal-primary)' : 'var(--bg-primary)',
            color: activeTiming === t ? 'white' : 'var(--text-secondary)',
          }"
          @click="activeTiming = activeTiming === t ? null : t"
        >
          {{ TIMING_LABELS[t] || t }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-6 text-sm" :style="{ color: 'var(--text-secondary)' }">
      Chargement des recommandations...
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-6 text-sm text-red-accent">
      {{ error }}
    </div>

    <!-- Empty -->
    <div v-else-if="filteredRecommendations.length === 0" class="text-center py-6">
      <div class="text-3xl mb-2">🍽️</div>
      <div class="text-sm" :style="{ color: 'var(--text-secondary)' }">Aucune recommandation disponible</div>
    </div>

    <!-- Cards list -->
    <div v-else class="flex flex-col gap-3">
      <MealRecommendationCard
        v-for="rec in filteredRecommendations"
        :key="rec.id"
        :recommendation="rec"
        @select="onSelect"
      />
    </div>

    <!-- Detail Modal -->
    <MealDetailModal
      v-if="selectedRec"
      :recommendation="selectedRec"
      :fast-id="fastId"
      @close="selectedRec = null"
      @logged="onLogged"
    />
  </div>
</template>
