<script setup lang="ts">
import type { Fast } from '../types'

defineProps<{ fast: Fast }>()

function duration(fast: Fast): string {
  if (!fast.ended) return 'En cours'
  const ms = new Date(fast.ended).getTime() - new Date(fast.started).getTime()
  const h = Math.floor(ms / 3600000)
  const m = Math.floor((ms % 3600000) / 60000)
  return `${h}h ${m}m`
}

function weightLoss(fast: Fast): string | null {
  if (fast.weight_before && fast.weight_after) {
    const diff = fast.weight_before - fast.weight_after
    return diff > 0 ? `-${diff.toFixed(1)} kg` : `+${Math.abs(diff).toFixed(1)} kg`
  }
  return null
}

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<template>
  <router-link :to="`/fast/${fast.id}`" class="block no-underline">
    <div class="rounded-2xl p-4 shadow-sm transition-shadow hover:shadow-md"
      :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }">
      <div class="flex justify-between items-start mb-2">
        <span class="text-sm font-semibold px-2 py-0.5 rounded-lg bg-teal-primary/10 text-teal-primary">{{ fast.type }}</span>
        <span class="text-xs px-2 py-0.5 rounded-lg" :class="fast.completed ? 'bg-green-100 text-green-700' : fast.ended ? 'bg-gray-100 text-gray-600' : 'bg-orange-100 text-orange-700'">
          {{ fast.completed ? 'Terminé' : fast.ended ? 'Arrêté' : 'En cours' }}
        </span>
      </div>
      <div class="text-sm" :style="{ color: 'var(--text-secondary)' }">{{ formatDate(fast.started) }}</div>
      <div class="flex gap-4 mt-2 text-sm">
        <span>{{ duration(fast) }}</span>
        <span v-if="weightLoss(fast)" class="font-semibold">{{ weightLoss(fast) }}</span>
      </div>
    </div>
  </router-link>
</template>
