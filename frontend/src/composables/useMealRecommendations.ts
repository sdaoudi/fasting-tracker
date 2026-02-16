import { ref } from 'vue'
import { getMealSuggestions, getMealRecommendationCategories } from '../api/client'
import type { MealRecommendation, CategoryCount } from '../types'

export function useMealRecommendations() {
  const recommendations = ref<MealRecommendation[]>([])
  const categories = ref<CategoryCount[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchSuggestions(params: {
    fast_id?: number
    fast_duration?: string
    phase?: string
    meal_timing?: string
    limit?: number
  } = {}) {
    loading.value = true
    error.value = null
    try {
      recommendations.value = await getMealSuggestions(params)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Erreur inconnue'
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    try {
      categories.value = await getMealRecommendationCategories()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Erreur inconnue'
    }
  }

  return { recommendations, categories, loading, error, fetchSuggestions, fetchCategories }
}

export function getMealTimingFromHour(): string {
  const h = new Date().getHours()
  if (h < 11) return 'petit_dejeuner'
  if (h < 15) return 'dejeuner'
  if (h < 18) return 'collation'
  return 'diner'
}

export const CATEGORY_LABELS: Record<string, string> = {
  rupture_jeune: 'Rupture de jeûne',
  repas_fenetre: 'Fenêtre alimentaire',
  reprise_progressive: 'Reprise progressive',
}

export const DIFFICULTY_LABELS: Record<string, string> = {
  facile: 'Facile',
  moyen: 'Moyen',
  'avancé': 'Avancé',
}

export const DIGESTIBILITY_COLORS: Record<string, string> = {
  'très_facile': '#10b981',
  facile: '#f59e0b',
  moyen: '#ef4444',
}

export const TIMING_LABELS: Record<string, string> = {
  petit_dejeuner: 'Petit-déjeuner',
  dejeuner: 'Déjeuner',
  diner: 'Dîner',
  collation: 'Collation',
}
