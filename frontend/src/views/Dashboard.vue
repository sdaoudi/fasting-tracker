<script setup lang="ts">
import { ref, shallowRef, onMounted, computed } from 'vue'
import CircularProgress from '../components/CircularProgress.vue'
import PhaseIndicator from '../components/PhaseIndicator.vue'
import StatCard from '../components/StatCard.vue'
import WeightChart from '../components/WeightChart.vue'
import MealRecommendationsList from '../components/MealRecommendationsList.vue'
import { getCurrentFast, getStats, getWeightTrend } from '../api/client'
import { useTimer, getPhase } from '../composables/useTimer'
import { saveActiveFast, loadActiveFast, clearActiveFast } from '../composables/useOfflineStorage'
import type { Fast, Stats, WeightTrend } from '../types'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentFast = ref<Fast | null>(null)
const stats = ref<Stats | null>(null)
const weightData = ref<WeightTrend[]>([])
const loading = ref(true)
const isOfflineData = ref(false)

const timer = shallowRef<ReturnType<typeof useTimer> | null>(null)
const elapsedHours = computed(() => timer.value ? timer.value.elapsed.value / 3600000 : 0)

onMounted(async () => {
  try {
    const [fast, s, w] = await Promise.all([
      getCurrentFast(),
      getStats(),
      getWeightTrend(30),
    ])
    currentFast.value = fast
    stats.value = s
    weightData.value = w
    if (fast && !fast.ended) {
      saveActiveFast(fast)
      timer.value = useTimer(fast.started, fast.target_hours)
    } else {
      clearActiveFast()
    }
  } catch {
    // Offline fallback: load active fast from localStorage
    const cached = loadActiveFast()
    if (cached && !cached.ended) {
      currentFast.value = cached
      timer.value = useTimer(cached.started, cached.target_hours)
      isOfflineData.value = true
    }
  } finally {
    loading.value = false
  }
})

function goToFast() {
  if (currentFast.value) router.push(`/fast/${currentFast.value.id}`)
}
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">Fasting Tracker</h1>

    <div v-if="loading" class="text-center py-12" :style="{ color: 'var(--text-secondary)' }">Chargement...</div>

    <template v-else>
      <!-- Active fast -->
      <div v-if="currentFast && timer" class="rounded-2xl p-6 mb-6 text-center shadow-sm"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="text-sm font-medium mb-1" :style="{ color: 'var(--text-secondary)' }">Jeûne {{ currentFast.type }} en cours</div>

        <div class="flex justify-center my-4" @click="goToFast" style="cursor: pointer;">
          <CircularProgress :progress="timer.progress.value" :size="200" :color="getPhase(elapsedHours).color">
            <div class="text-center">
              <div class="text-3xl font-bold font-mono">{{ timer.elapsedFormatted.value }}</div>
              <div class="text-xs mt-1" :style="{ color: 'var(--text-secondary)' }">
                {{ timer.isOvertime.value ? 'Dépassé !' : `Reste : ${timer.remainingFormatted.value}` }}
              </div>
            </div>
          </CircularProgress>
        </div>

        <PhaseIndicator :elapsed-hours="elapsedHours" class="mb-4" />

        <div class="flex gap-3">
          <router-link :to="`/fast/${currentFast.id}`"
            class="flex-1 py-2.5 rounded-xl font-semibold text-center no-underline bg-teal-primary text-white">
            Voir détails
          </router-link>
        </div>
      </div>

      <!-- No active fast -->
      <div v-else class="rounded-2xl p-6 mb-6 text-center shadow-sm"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="text-4xl mb-3">{{'🍽️'}}</div>
        <div class="text-lg font-semibold mb-1">Aucun jeûne actif</div>
        <div class="text-sm mb-4" :style="{ color: 'var(--text-secondary)' }">Commencez un nouveau jeûne</div>
        <div class="flex gap-2 justify-center flex-wrap">
          <router-link to="/start" class="px-4 py-2 rounded-xl font-semibold no-underline bg-teal-primary text-white">
            Démarrer un jeûne
          </router-link>
        </div>
      </div>

      <!-- Quick stats -->
      <div v-if="stats" class="grid grid-cols-2 gap-3 mb-6">
        <StatCard icon="⏱️" label="Jeûnes total" :value="stats.total_fasts" />
        <StatCard icon="✅" label="Complétés" :value="stats.completed_fasts" />
        <StatCard icon="📏" label="Durée moyenne" :value="stats.avg_duration_hours ? stats.avg_duration_hours + 'h' : '-'" />
        <StatCard icon="⚖️" label="Poids perdu" :value="stats.total_weight_lost ? stats.total_weight_lost.toFixed(1) + ' kg' : '-'" />
      </div>

      <!-- Meal Recommendations -->
      <div class="rounded-2xl p-4 shadow-sm mb-6"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="flex items-center justify-between mb-3">
          <div class="text-sm font-semibold">Repas recommandés</div>
          <router-link to="/meals" class="text-xs no-underline" style="color: var(--color-teal-primary)">
            Voir tout
          </router-link>
        </div>
        <MealRecommendationsList
          :fast-id="currentFast?.id"
          :fast-duration="currentFast?.type"
          :compact="true"
        />
      </div>

      <!-- Weight chart -->
      <div class="rounded-2xl p-4 shadow-sm mb-6"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="text-sm font-semibold mb-2">Poids (30 derniers jours)</div>
        <WeightChart :data="weightData" :mini="true" />
      </div>

      <!-- Quick links -->
      <div class="flex gap-3">
        <router-link to="/history" class="flex-1 py-3 rounded-xl text-center no-underline text-sm font-medium"
          :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }">
          {{'📋'}} Historique
        </router-link>
        <router-link to="/weight" class="flex-1 py-3 rounded-xl text-center no-underline text-sm font-medium"
          :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }">
          {{'⚖️'}} Poids
        </router-link>
      </div>
    </template>
  </div>
</template>
