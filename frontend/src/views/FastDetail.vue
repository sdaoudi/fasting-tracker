<script setup lang="ts">
import { ref, shallowRef, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CircularProgress from '../components/CircularProgress.vue'
import PhaseIndicator from '../components/PhaseIndicator.vue'
import BodyStateCard from '../components/BodyStateCard.vue'
import MoodSelector from '../components/MoodSelector.vue'
import SliderInput from '../components/SliderInput.vue'
import { getFast, updateFast, getLogs, createLog, getMeals, createMeal } from '../api/client'
import { useTimer, getPhase, formatDuration } from '../composables/useTimer'
import { useBodyState } from '../composables/useBodyState'
import { loadActiveFast, clearActiveFast } from '../composables/useOfflineStorage'
import { useOnlineStatus } from '../composables/useOnlineStatus'
import type { Fast, DailyLog, Meal } from '../types'

const route = useRoute()
const router = useRouter()
const fastId = Number(route.params.id)
const { isOnline } = useOnlineStatus()

const fast = ref<Fast | null>(null)
const logs = ref<DailyLog[]>([])
const meals = ref<Meal[]>([])
const loading = ref(true)
const isOfflineData = ref(false)
const timer = shallowRef<ReturnType<typeof useTimer> | null>(null)
const elapsedHours = computed(() => timer.value ? timer.value.elapsed.value / 3600000 : 0)
const isActive = computed(() => fast.value && !fast.value.ended)
const { state: bodyState } = useBodyState(elapsedHours)

// Log form
const logWater = ref(2)
const logElectrolytes = ref(false)
const logEnergy = ref(5)
const logHunger = ref(5)
const logMood = ref('')
const logNotes = ref('')
const showLogForm = ref(false)
const submittingLog = ref(false)

// End fast
const showEndForm = ref(false)
const endDateTime = ref('')
const weightAfter = ref('')
const submittingEnd = ref(false)

function formatForDatetimeLocal(date: Date): string {
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function openEndForm() {
  endDateTime.value = formatForDatetimeLocal(new Date())
  showEndForm.value = true
}

// Meal form
const showMealForm = ref(false)
const mealType = ref('repas')
const mealName = ref('')
const mealCalories = ref('')
const mealBreaking = ref(false)
const mealNotes = ref('')
const submittingMeal = ref(false)

onMounted(async () => {
  try {
    const [f, l, m] = await Promise.all([
      getFast(fastId),
      getLogs(fastId),
      getMeals(fastId),
    ])
    fast.value = f
    logs.value = l
    meals.value = m
    if (f && !f.ended) {
      timer.value = useTimer(f.started, f.target_hours)
    }
  } catch {
    // Offline fallback: load active fast from localStorage
    const cached = loadActiveFast()
    if (cached && cached.id === fastId && !cached.ended) {
      fast.value = cached
      timer.value = useTimer(cached.started, cached.target_hours)
      isOfflineData.value = true
    }
  } finally {
    loading.value = false
  }
})

async function endFast() {
  submittingEnd.value = true
  try {
    const data: Record<string, unknown> = {
      ended: new Date(endDateTime.value).toISOString(),
      completed: true,
    }
    if (weightAfter.value) data.weight_after = parseFloat(weightAfter.value)
    await updateFast(fastId, data)
    fast.value = await getFast(fastId)
    timer.value?.stop()
    timer.value = null
    clearActiveFast()
    showEndForm.value = false
  } finally {
    submittingEnd.value = false
  }
}

async function submitLog() {
  submittingLog.value = true
  try {
    await createLog(fastId, {
      water_liters: logWater.value,
      electrolytes: logElectrolytes.value,
      energy_level: logEnergy.value,
      hunger_level: logHunger.value,
      mood: logMood.value || undefined,
      notes: logNotes.value || undefined,
    })
    logs.value = await getLogs(fastId)
    showLogForm.value = false
    logNotes.value = ''
  } finally {
    submittingLog.value = false
  }
}

async function submitMeal() {
  submittingMeal.value = true
  try {
    await createMeal(fastId, {
      meal_type: mealType.value,
      meal_name: mealName.value || undefined,
      calories: mealCalories.value ? parseInt(mealCalories.value) : undefined,
      is_breaking_fast: mealBreaking.value,
      notes: mealNotes.value || undefined,
    })
    meals.value = await getMeals(fastId)
    showMealForm.value = false
    mealName.value = ''
    mealCalories.value = ''
    mealNotes.value = ''
  } finally {
    submittingMeal.value = false
  }
}

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function formatElapsed(f: Fast): string {
  if (f.ended) {
    return formatDuration(new Date(f.ended).getTime() - new Date(f.started).getTime())
  }
  return ''
}
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-6">
    <button @click="router.back()" class="mb-4 text-sm flex items-center gap-1 border-0 bg-transparent cursor-pointer"
      :style="{ color: 'var(--text-secondary)' }">
      &larr; Retour
    </button>

    <div v-if="loading" class="text-center py-12" :style="{ color: 'var(--text-secondary)' }">Chargement...</div>

    <template v-else-if="fast">
      <!-- Timer section (active) -->
      <div v-if="isActive && timer" class="rounded-2xl p-6 mb-6 text-center shadow-sm"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="text-sm font-medium mb-1" :style="{ color: 'var(--text-secondary)' }">Jeûne {{ fast.type }}</div>

        <div class="flex justify-center my-4">
          <CircularProgress :progress="timer.progress.value" :size="220" :stroke-width="14" :color="getPhase(elapsedHours).color">
            <div class="text-center">
              <div class="text-3xl font-bold font-mono">{{ timer.elapsedFormatted.value }}</div>
              <div class="text-xs mt-1" :style="{ color: 'var(--text-secondary)' }">
                {{ timer.isOvertime.value ? 'Objectif dépassé !' : `Reste : ${timer.remainingFormatted.value}` }}
              </div>
            </div>
          </CircularProgress>
        </div>

        <PhaseIndicator :elapsed-hours="elapsedHours" class="mb-4" />

        <!-- Phase timeline -->
        <div class="flex gap-1 mb-4">
          <div v-for="(p, i) in [{h:12, start:0, c:'#10b981'}, {h:24, start:12, c:'#f59e0b'}, {h:36, start:24, c:'#ef4444'}, {h:999, start:36, c:'#8b5cf6'}]" :key="i"
            class="flex-1 h-2 rounded-full transition-colors"
            :style="{ backgroundColor: elapsedHours >= p.h ? p.c : elapsedHours > p.start ? p.c + '80' : 'var(--border-color)' }">
          </div>
        </div>

        <button @click="openEndForm()" :disabled="!isOnline"
          class="w-full py-2.5 rounded-xl font-semibold text-white bg-red-accent border-0 cursor-pointer disabled:opacity-50"
          :title="!isOnline ? 'Connexion requise' : ''">
          {{ isOnline ? 'Terminer le Jeûne' : 'Terminer le Jeûne (hors ligne)' }}
        </button>
      </div>

      <!-- Body State Information Card -->
      <div v-if="isActive && timer" class="mb-6">
        <BodyStateCard :state="bodyState" :elapsed-hours="elapsedHours" />
      </div>

      <!-- Completed fast summary -->
      <div v-else class="rounded-2xl p-6 mb-6 shadow-sm"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <div class="flex justify-between items-center mb-3">
          <span class="text-sm font-semibold px-2 py-0.5 rounded-lg bg-teal-primary/10 text-teal-primary">{{ fast.type }}</span>
          <span class="text-xs px-2 py-0.5 rounded-lg" :class="fast.completed ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'">
            {{ fast.completed ? 'Terminé' : 'Arrêté' }}
          </span>
        </div>
        <div class="text-sm mb-1"><strong>Début :</strong> {{ formatDate(fast.started) }}</div>
        <div v-if="fast.ended" class="text-sm mb-1"><strong>Fin :</strong> {{ formatDate(fast.ended) }}</div>
        <div v-if="fast.ended" class="text-sm mb-1"><strong>Durée :</strong> {{ formatElapsed(fast) }}</div>
        <div v-if="fast.weight_before" class="text-sm mb-1"><strong>Poids avant :</strong> {{ fast.weight_before }} kg</div>
        <div v-if="fast.weight_after" class="text-sm mb-1"><strong>Poids après :</strong> {{ fast.weight_after }} kg</div>
        <div v-if="fast.notes" class="text-sm mt-2 italic" :style="{ color: 'var(--text-secondary)' }">{{ fast.notes }}</div>
      </div>

      <!-- End fast modal -->
      <div v-if="showEndForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="rounded-2xl p-6 w-full max-w-sm" :style="{ backgroundColor: 'var(--bg-card)' }">
          <h3 class="text-lg font-bold mb-4">Terminer le Jeûne</h3>
          <div class="mb-4">
            <label class="text-sm font-medium mb-2 block">Date et heure de fin</label>
            <input v-model="endDateTime" type="datetime-local"
              class="w-full px-4 py-2.5 rounded-xl border outline-none appearance-none"
              style="-webkit-appearance: none; -moz-appearance: none; font-size: 16px; min-height: 44px;"
              :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }" />
          </div>
          <div class="mb-4">
            <label class="text-sm font-medium mb-2 block">Poids après (optionnel)</label>
            <input v-model="weightAfter" type="number" step="0.1" placeholder="ex: 84.0"
              class="w-full px-4 py-2.5 rounded-xl border outline-none"
              :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }" />
          </div>
          <div class="flex gap-2">
            <button @click="showEndForm = false" class="flex-1 py-2.5 rounded-xl border cursor-pointer"
              :style="{ borderColor: 'var(--border-color)', backgroundColor: 'transparent', color: 'var(--text-primary)' }">Annuler</button>
            <button @click="endFast" :disabled="submittingEnd"
              class="flex-1 py-2.5 rounded-xl font-semibold text-white bg-red-accent border-0 cursor-pointer disabled:opacity-50">
              {{ submittingEnd ? '...' : 'Confirmer' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Daily log form toggle -->
      <div v-if="isActive" class="mb-6">
        <button @click="showLogForm = !showLogForm"
          class="w-full py-2.5 rounded-xl font-semibold border-2 border-teal-primary text-teal-primary bg-transparent cursor-pointer">
          {{ showLogForm ? 'Masquer' : 'Ajouter un journal du jour' }}
        </button>
      </div>

      <!-- Daily log form -->
      <div v-if="showLogForm" class="rounded-2xl p-5 mb-6 shadow-sm"
        :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
        <h3 class="text-lg font-bold mb-4">Journal du jour</h3>

        <SliderInput v-model="logWater" :min="0" :max="5" :step="0.5" label="Eau (litres)" unit="L" class="mb-4" />

        <div class="flex items-center gap-3 mb-4">
          <label class="text-sm font-medium">Électrolytes pris ?</label>
          <button @click="logElectrolytes = !logElectrolytes"
            class="w-12 h-6 rounded-full relative cursor-pointer border-0 transition-colors"
            :style="{ backgroundColor: logElectrolytes ? '#0d9488' : 'var(--border-color)' }">
            <span class="absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform"
              :style="{ left: logElectrolytes ? '26px' : '2px' }"></span>
          </button>
        </div>

        <SliderInput v-model="logEnergy" :min="1" :max="10" label="Énergie" class="mb-4" />
        <SliderInput v-model="logHunger" :min="1" :max="10" label="Faim" class="mb-4" />

        <div class="mb-4">
          <label class="text-sm font-medium mb-2 block">Humeur</label>
          <MoodSelector v-model="logMood" />
        </div>

        <div class="mb-4">
          <label class="text-sm font-medium mb-2 block">Notes</label>
          <textarea v-model="logNotes" rows="2" placeholder="Comment vous sentez-vous ?"
            class="w-full px-3 py-2 rounded-xl border outline-none resize-none text-sm"
            :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }"></textarea>
        </div>

        <button @click="submitLog" :disabled="submittingLog || !isOnline"
          class="w-full py-2.5 rounded-xl font-semibold text-white bg-teal-primary border-0 cursor-pointer disabled:opacity-50">
          {{ !isOnline ? 'Hors ligne' : submittingLog ? 'Enregistrement...' : 'Enregistrer' }}
        </button>
      </div>

      <!-- Log history -->
      <div v-if="logs.length > 0" class="mb-6">
        <h3 class="text-lg font-bold mb-3">Journaux</h3>
        <div v-for="log in logs" :key="log.id" class="rounded-xl p-3 mb-2 text-sm"
          :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
          <div class="flex justify-between mb-1">
            <span class="font-medium">{{ new Date(log.log_date).toLocaleDateString('fr-FR') }}</span>
            <span v-if="log.mood">{{ {'happy':'😊','neutral':'😐','struggling':'😣','nauseous':'🤢','tired':'😴','strong':'💪'}[log.mood] || log.mood }}</span>
          </div>
          <div class="flex gap-3" :style="{ color: 'var(--text-secondary)' }">
            <span v-if="log.water_liters">💧 {{ log.water_liters }}L</span>
            <span v-if="log.electrolytes">⚡ Électrolytes</span>
            <span v-if="log.energy_level">⚡ {{ log.energy_level }}/10</span>
            <span v-if="log.hunger_level">🍽️ {{ log.hunger_level }}/10</span>
          </div>
          <div v-if="log.notes" class="mt-1 italic" :style="{ color: 'var(--text-secondary)' }">{{ log.notes }}</div>
        </div>
      </div>

      <!-- Meals section -->
      <div class="mb-6">
        <div class="flex justify-between items-center mb-3">
          <h3 class="text-lg font-bold">Repas</h3>
          <button @click="showMealForm = !showMealForm"
            class="text-sm text-teal-primary font-semibold border-0 bg-transparent cursor-pointer">
            {{ showMealForm ? 'Masquer' : '+ Ajouter' }}
          </button>
        </div>

        <!-- Meal form -->
        <div v-if="showMealForm" class="rounded-xl p-4 mb-3"
          :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
          <select v-model="mealType" class="w-full px-3 py-2 rounded-xl border mb-3 outline-none"
            :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }">
            <option value="petit-dejeuner">Petit-déjeuner</option>
            <option value="dejeuner">Déjeuner</option>
            <option value="diner">Dîner</option>
            <option value="collation">Collation</option>
            <option value="repas">Repas</option>
          </select>
          <input v-model="mealName" placeholder="Nom du repas" class="w-full px-3 py-2 rounded-xl border mb-3 outline-none"
            :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }" />
          <input v-model="mealCalories" type="number" placeholder="Calories (optionnel)" class="w-full px-3 py-2 rounded-xl border mb-3 outline-none"
            :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }" />
          <div class="flex items-center gap-2 mb-3">
            <input type="checkbox" v-model="mealBreaking" id="breaking" />
            <label for="breaking" class="text-sm">Rupture de jeûne ?</label>
          </div>
          <button @click="submitMeal" :disabled="submittingMeal || !isOnline"
            class="w-full py-2 rounded-xl font-semibold text-white bg-teal-primary border-0 cursor-pointer text-sm disabled:opacity-50">
            {{ !isOnline ? 'Hors ligne' : submittingMeal ? '...' : 'Enregistrer le repas' }}
          </button>
        </div>

        <!-- Meals list -->
        <div v-for="meal in meals" :key="meal.id" class="rounded-xl p-3 mb-2 text-sm"
          :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
          <div class="flex justify-between">
            <span class="font-medium">{{ meal.meal_name || meal.meal_type }}</span>
            <span v-if="meal.calories" :style="{ color: 'var(--text-secondary)' }">{{ meal.calories }} cal</span>
          </div>
          <div v-if="meal.is_breaking_fast" class="text-xs text-orange-accent mt-1">Rupture de jeûne</div>
        </div>
        <div v-if="meals.length === 0" class="text-sm" :style="{ color: 'var(--text-secondary)' }">Aucun repas enregistré</div>
      </div>
    </template>
  </div>
</template>
