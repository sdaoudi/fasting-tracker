<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getRecentMeals } from '../api/client'
import type { Meal } from '../types'

const meals = ref<Meal[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    meals.value = await getRecentMeals(50)
  } finally {
    loading.value = false
  }
})

const suggestions = [
  { name: 'Bouillon d\'os', calories: 40, type: 'rupture' },
  { name: 'Avocat + oeufs', calories: 350, type: 'repas' },
  { name: 'Salade de poulet', calories: 400, type: 'repas' },
  { name: 'Soupe de legumes', calories: 150, type: 'rupture' },
  { name: 'Saumon + riz', calories: 500, type: 'repas' },
  { name: 'Yaourt grec + noix', calories: 250, type: 'collation' },
]

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">Repas</h1>

    <!-- Suggestions -->
    <div class="rounded-2xl p-4 mb-6 shadow-sm"
      :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
      <div class="text-sm font-semibold mb-3">Suggestions de repas sains</div>
      <div class="grid grid-cols-2 gap-2">
        <div v-for="s in suggestions" :key="s.name" class="rounded-xl p-3"
          :style="{ backgroundColor: 'var(--bg-primary)' }">
          <div class="text-sm font-medium">{{ s.name }}</div>
          <div class="text-xs" :style="{ color: 'var(--text-secondary)' }">{{ s.calories }} cal - {{ s.type }}</div>
        </div>
      </div>
    </div>

    <!-- Recent meals -->
    <div>
      <div class="text-sm font-semibold mb-3">Repas recents</div>

      <div v-if="loading" class="text-center py-8" :style="{ color: 'var(--text-secondary)' }">Chargement...</div>

      <div v-else-if="meals.length === 0" class="text-center py-8">
        <div class="text-4xl mb-3">{{'🍽️'}}</div>
        <div :style="{ color: 'var(--text-secondary)' }">Aucun repas enregistre</div>
        <div class="text-sm mt-1" :style="{ color: 'var(--text-secondary)' }">Ajoutez des repas depuis la page d'un jeune</div>
      </div>

      <div v-else class="flex flex-col gap-2">
        <div v-for="meal in meals" :key="meal.id" class="rounded-xl p-3"
          :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
          <div class="flex justify-between items-start">
            <div>
              <div class="text-sm font-medium">{{ meal.meal_name || meal.meal_type }}</div>
              <div class="text-xs" :style="{ color: 'var(--text-secondary)' }">
                {{ meal.meal_type }} <span v-if="meal.meal_time">- {{ formatDate(meal.meal_time) }}</span>
              </div>
            </div>
            <div class="text-right">
              <div v-if="meal.calories" class="text-sm font-semibold">{{ meal.calories }} cal</div>
              <div v-if="meal.is_breaking_fast" class="text-xs text-orange-accent">Rupture</div>
            </div>
          </div>
          <div v-if="meal.notes" class="text-xs mt-1 italic" :style="{ color: 'var(--text-secondary)' }">{{ meal.notes }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
