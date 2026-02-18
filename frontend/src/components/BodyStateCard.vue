<script setup lang="ts">
import { ref } from 'vue'
import type { BodyState } from '../composables/useBodyState'

const props = defineProps<{
  state: BodyState
  elapsedHours: number
}>()

const expanded = ref(false)
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
    <!-- Header with phase color -->
    <div
      class="px-4 py-4 flex items-center gap-3"
      :style="{ backgroundColor: state.phaseColor + '18', borderLeft: `4px solid ${state.phaseColor}` }"
    >
      <span class="text-3xl">{{ state.phaseIcon }}</span>
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <span
            class="text-xs font-semibold px-2 py-0.5 rounded-full text-white"
            :style="{ backgroundColor: state.phaseColor }"
          >
            {{ state.phase }}
          </span>
          <span class="text-xs text-gray-500">{{ Math.floor(elapsedHours) }}h de jeûne</span>
        </div>
        <h3 class="font-bold text-gray-800 text-base mt-0.5 leading-tight">{{ state.headline }}</h3>
      </div>
    </div>

    <div class="px-4 py-4 space-y-4">
      <!-- Processus actifs -->
      <div>
        <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Ce que fait ton corps</h4>
        <div class="space-y-2">
          <div
            v-for="process in state.processes"
            :key="process.name"
            class="flex items-center gap-3 py-2 px-3 rounded-xl"
            :class="{
              'bg-green-50': process.status === 'active',
              'bg-yellow-50': process.status === 'starting',
              'bg-gray-50': process.status === 'inactive',
            }"
          >
            <span class="text-xl flex-shrink-0">{{ process.icon }}</span>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-gray-800">{{ process.name }}</span>
                <span
                  class="text-xs px-1.5 py-0.5 rounded-full font-medium"
                  :class="{
                    'bg-green-100 text-green-700': process.status === 'active',
                    'bg-yellow-100 text-yellow-700': process.status === 'starting',
                    'bg-gray-100 text-gray-500': process.status === 'inactive',
                  }"
                >
                  {{ process.status === 'active' ? 'Actif' : process.status === 'starting' ? 'En démarrage' : 'Inactif' }}
                </span>
              </div>
              <p class="text-xs text-gray-500 mt-0.5">{{ process.detail }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Description (expandable) -->
      <div>
        <button
          class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
          @click="expanded = !expanded"
        >
          <svg
            class="w-4 h-4 transition-transform duration-200"
            :class="{ 'rotate-180': expanded }"
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          {{ expanded ? 'Moins d\'infos' : 'En savoir plus' }}
        </button>
        <div
          v-if="expanded"
          class="mt-2 text-sm text-gray-600 leading-relaxed bg-gray-50 rounded-xl p-3"
        >
          {{ state.description }}
        </div>
      </div>

      <!-- Tips -->
      <div v-if="state.tips.length">
        <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">💡 Conseils</h4>
        <ul class="space-y-1">
          <li
            v-for="tip in state.tips"
            :key="tip"
            class="text-sm text-gray-600 flex items-start gap-2"
          >
            <span class="text-gray-300 mt-0.5 flex-shrink-0">›</span>
            <span>{{ tip }}</span>
          </li>
        </ul>
      </div>

      <!-- Prochaine phase -->
      <div v-if="state.nextPhase" class="rounded-xl border border-dashed border-gray-200 p-3">
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-semibold text-gray-500">Prochaine phase</span>
          <span class="text-xs font-bold text-gray-700">
            dans {{ state.nextPhase.hoursUntil < 1
              ? Math.round(state.nextPhase.hoursUntil * 60) + ' min'
              : state.nextPhase.hoursUntil.toFixed(1) + 'h' }}
          </span>
        </div>
        <!-- Progress bar -->
        <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden mb-2">
          <div
            class="h-full rounded-full transition-all duration-1000"
            :style="{
              backgroundColor: state.phaseColor,
              width: Math.max(2, Math.min(100, (1 - state.nextPhase.hoursUntil / (state.nextPhase.hoursUntil + (elapsedHours % 8))) * 100)) + '%'
            }"
          />
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-700">{{ state.nextPhase.name }}</span>
        </div>
        <p class="text-xs text-gray-500 mt-0.5">{{ state.nextPhase.preview }}</p>
      </div>
    </div>
  </div>
</template>
