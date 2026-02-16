<script setup lang="ts">
import type { MealRecommendation } from '../types'
import { DIGESTIBILITY_COLORS, CATEGORY_LABELS, TIMING_LABELS } from '../composables/useMealRecommendations'

const props = defineProps<{
  recommendation: MealRecommendation
}>()

const emit = defineEmits<{
  select: [rec: MealRecommendation]
}>()

function digestibilityLabel(d: string | null): string {
  if (!d) return ''
  const map: Record<string, string> = { 'très_facile': 'Tres facile', facile: 'Facile', moyen: 'Moyen' }
  return map[d] || d
}

function difficultyIcon(d: string | null): string {
  if (!d) return ''
  const map: Record<string, string> = { facile: '🟢', moyen: '🟡', 'avancé': '🔴' }
  return map[d] || '⚪'
}
</script>

<template>
  <div
    class="rounded-2xl p-4 shadow-sm cursor-pointer transition-transform hover:scale-[1.02] active:scale-[0.98]"
    :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }"
    @click="emit('select', props.recommendation)"
  >
    <!-- Header: name + category badge -->
    <div class="flex items-start justify-between gap-2 mb-2">
      <div class="font-semibold text-sm leading-tight">{{ recommendation.name }}</div>
      <span
        v-if="recommendation.digestibility"
        class="shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full text-white"
        :style="{ backgroundColor: DIGESTIBILITY_COLORS[recommendation.digestibility] || '#888' }"
      >
        {{ digestibilityLabel(recommendation.digestibility) }}
      </span>
    </div>

    <!-- Description (truncated) -->
    <div
      v-if="recommendation.description"
      class="text-xs mb-3 line-clamp-2"
      :style="{ color: 'var(--text-secondary)' }"
    >
      {{ recommendation.description }}
    </div>

    <!-- Macros bar -->
    <div v-if="recommendation.macros" class="flex gap-3 text-[11px] mb-3">
      <div v-if="recommendation.macros.calories" class="flex items-center gap-1">
        <span>🔥</span>
        <span class="font-semibold">{{ recommendation.macros.calories }}</span>
        <span :style="{ color: 'var(--text-secondary)' }">cal</span>
      </div>
      <div v-if="recommendation.macros.protein" class="flex items-center gap-1">
        <span>💪</span>
        <span class="font-semibold">{{ recommendation.macros.protein }}g</span>
        <span :style="{ color: 'var(--text-secondary)' }">prot</span>
      </div>
      <div v-if="recommendation.macros.carbs" class="flex items-center gap-1">
        <span>🌾</span>
        <span class="font-semibold">{{ recommendation.macros.carbs }}g</span>
      </div>
      <div v-if="recommendation.macros.fat" class="flex items-center gap-1">
        <span>🫒</span>
        <span class="font-semibold">{{ recommendation.macros.fat }}g</span>
      </div>
    </div>

    <!-- Footer: timing, prep time, difficulty -->
    <div class="flex items-center gap-3 text-[11px]" :style="{ color: 'var(--text-secondary)' }">
      <div v-if="recommendation.preparation_time" class="flex items-center gap-1">
        <span>⏱️</span>
        <span>{{ recommendation.preparation_time }} min</span>
      </div>
      <div v-if="recommendation.difficulty" class="flex items-center gap-1">
        <span>{{ difficultyIcon(recommendation.difficulty) }}</span>
        <span>{{ recommendation.difficulty }}</span>
      </div>
      <div v-if="recommendation.meal_timing" class="flex items-center gap-1">
        <span>🍽️</span>
        <span>{{ TIMING_LABELS[recommendation.meal_timing] || recommendation.meal_timing }}</span>
      </div>
      <div v-if="recommendation.category" class="ml-auto text-[10px] px-2 py-0.5 rounded-full"
        :style="{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-secondary)' }">
        {{ CATEGORY_LABELS[recommendation.category] || recommendation.category }}
      </div>
    </div>
  </div>
</template>
