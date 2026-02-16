<script setup lang="ts">
import { ref, computed } from 'vue'
import type { MealRecommendation } from '../types'
import { createMeal } from '../api/client'
import { CATEGORY_LABELS, DIGESTIBILITY_COLORS, TIMING_LABELS } from '../composables/useMealRecommendations'

const props = defineProps<{
  recommendation: MealRecommendation
  fastId?: number | null
}>()

const emit = defineEmits<{
  close: []
  logged: []
}>()

const checkedIngredients = ref<Set<number>>(new Set())
const logging = ref(false)
const logged = ref(false)

function toggleIngredient(index: number) {
  if (checkedIngredients.value.has(index)) {
    checkedIngredients.value.delete(index)
  } else {
    checkedIngredients.value.add(index)
  }
}

const macros = computed(() => props.recommendation.macros)
const totalMacroGrams = computed(() => {
  if (!macros.value) return 0
  return (macros.value.protein || 0) + (macros.value.carbs || 0) + (macros.value.fat || 0)
})

function macroPercent(value: number | null): number {
  if (!value || !totalMacroGrams.value) return 0
  return Math.round((value / totalMacroGrams.value) * 100)
}

function digestibilityLabel(d: string | null): string {
  if (!d) return ''
  const map: Record<string, string> = { 'très_facile': 'Très facile', facile: 'Facile', moyen: 'Moyen' }
  return map[d] || d
}

async function logMeal() {
  if (!props.fastId || logging.value) return
  logging.value = true
  try {
    await createMeal(props.fastId, {
      meal_type: props.recommendation.category === 'rupture_jeune' ? 'rupture' : 'repas',
      meal_name: props.recommendation.name,
      ingredients: props.recommendation.ingredients,
      calories: props.recommendation.macros?.calories,
      is_breaking_fast: props.recommendation.category === 'rupture_jeune',
      notes: `Recommandation: ${props.recommendation.name}`,
    })
    logged.value = true
    emit('logged')
  } finally {
    logging.value = false
  }
}
</script>

<template>
  <!-- Backdrop -->
  <div class="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
    <div class="absolute inset-0 bg-black/50" @click="emit('close')"></div>

    <!-- Modal -->
    <div
      class="relative z-10 w-full max-w-lg max-h-[85vh] overflow-y-auto rounded-t-2xl sm:rounded-2xl p-5 pb-20 sm:pb-5 shadow-xl"
      :style="{ backgroundColor: 'var(--bg-card)' }"
    >
      <!-- Close button -->
      <button
        class="absolute top-3 right-3 w-8 h-8 rounded-full flex items-center justify-center text-lg"
        :style="{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-secondary)' }"
        @click="emit('close')"
      >
        ✕
      </button>

      <!-- Header -->
      <div class="pr-8 mb-4">
        <h2 class="text-lg font-bold">{{ recommendation.name }}</h2>
        <div class="flex items-center gap-2 mt-1 text-xs" :style="{ color: 'var(--text-secondary)' }">
          <span class="px-2 py-0.5 rounded-full" :style="{ backgroundColor: 'var(--bg-primary)' }">
            {{ CATEGORY_LABELS[recommendation.category] || recommendation.category }}
          </span>
          <span v-if="recommendation.meal_timing">
            {{ TIMING_LABELS[recommendation.meal_timing] || recommendation.meal_timing }}
          </span>
          <span v-if="recommendation.phase" class="font-medium">
            {{ recommendation.phase.replace('_', ' ') }}
          </span>
        </div>
      </div>

      <!-- Description -->
      <p
        v-if="recommendation.description"
        class="text-sm mb-4"
        :style="{ color: 'var(--text-secondary)' }"
      >
        {{ recommendation.description }}
      </p>

      <!-- Macros -->
      <div v-if="macros" class="rounded-xl p-4 mb-4" :style="{ backgroundColor: 'var(--bg-primary)' }">
        <div class="text-xs font-semibold mb-3">Informations nutritionnelles</div>
        <div class="grid grid-cols-4 gap-2 text-center mb-3">
          <div>
            <div class="text-lg font-bold">{{ macros.calories || '-' }}</div>
            <div class="text-[10px]" :style="{ color: 'var(--text-secondary)' }">cal</div>
          </div>
          <div>
            <div class="text-lg font-bold" style="color: #ef4444">{{ macros.protein || '-' }}</div>
            <div class="text-[10px]" :style="{ color: 'var(--text-secondary)' }">prot (g)</div>
          </div>
          <div>
            <div class="text-lg font-bold" style="color: #f59e0b">{{ macros.carbs || '-' }}</div>
            <div class="text-[10px]" :style="{ color: 'var(--text-secondary)' }">gluc (g)</div>
          </div>
          <div>
            <div class="text-lg font-bold" style="color: #3b82f6">{{ macros.fat || '-' }}</div>
            <div class="text-[10px]" :style="{ color: 'var(--text-secondary)' }">lip (g)</div>
          </div>
        </div>
        <!-- Macro bar -->
        <div v-if="totalMacroGrams > 0" class="h-2 rounded-full overflow-hidden flex">
          <div :style="{ width: macroPercent(macros.protein) + '%', backgroundColor: '#ef4444' }"></div>
          <div :style="{ width: macroPercent(macros.carbs) + '%', backgroundColor: '#f59e0b' }"></div>
          <div :style="{ width: macroPercent(macros.fat) + '%', backgroundColor: '#3b82f6' }"></div>
        </div>
      </div>

      <!-- Meta: prep time, difficulty, digestibility -->
      <div class="flex flex-wrap gap-3 mb-4 text-xs">
        <div v-if="recommendation.preparation_time" class="flex items-center gap-1 px-3 py-1.5 rounded-full"
          :style="{ backgroundColor: 'var(--bg-primary)' }">
          <span>⏱️</span> {{ recommendation.preparation_time }} min
        </div>
        <div v-if="recommendation.difficulty" class="flex items-center gap-1 px-3 py-1.5 rounded-full"
          :style="{ backgroundColor: 'var(--bg-primary)' }">
          {{ recommendation.difficulty === 'facile' ? '🟢' : recommendation.difficulty === 'moyen' ? '🟡' : '🔴' }}
          {{ recommendation.difficulty }}
        </div>
        <div v-if="recommendation.digestibility" class="flex items-center gap-1 px-3 py-1.5 rounded-full text-white font-medium"
          :style="{ backgroundColor: DIGESTIBILITY_COLORS[recommendation.digestibility] || '#888' }">
          {{ digestibilityLabel(recommendation.digestibility) }}
        </div>
      </div>

      <!-- Ingredients with checkboxes -->
      <div v-if="recommendation.ingredients?.length" class="mb-4">
        <div class="text-xs font-semibold mb-2">Ingrédients</div>
        <div class="flex flex-col gap-1.5">
          <label
            v-for="(ing, i) in recommendation.ingredients"
            :key="i"
            class="flex items-center gap-2 text-sm cursor-pointer py-1"
            :class="{ 'line-through opacity-50': checkedIngredients.has(i) }"
          >
            <input
              type="checkbox"
              :checked="checkedIngredients.has(i)"
              class="w-4 h-4 rounded accent-teal-primary"
              @change="toggleIngredient(i)"
            />
            {{ ing }}
          </label>
        </div>
      </div>

      <!-- Tips -->
      <div v-if="recommendation.tips" class="rounded-xl p-3 mb-5 text-sm"
        :style="{ backgroundColor: 'var(--bg-primary)' }">
        <div class="text-xs font-semibold mb-1">💡 Conseils</div>
        <div :style="{ color: 'var(--text-secondary)' }">{{ recommendation.tips }}</div>
      </div>

      <!-- Log meal button -->
      <button
        v-if="fastId && !logged"
        class="w-full py-3 rounded-xl font-semibold text-white transition-colors"
        :class="logging ? 'opacity-50' : ''"
        :style="{ backgroundColor: 'var(--color-teal-primary)' }"
        :disabled="logging"
        @click="logMeal"
      >
        {{ logging ? 'Enregistrement...' : "J'ai mangé ce repas" }}
      </button>
      <div
        v-if="logged"
        class="w-full py-3 rounded-xl font-semibold text-center text-white"
        style="background-color: #10b981"
      >
        ✓ Repas enregistré !
      </div>
    </div>
  </div>
</template>
