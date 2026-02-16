<script setup lang="ts">
import { getPhase } from '../composables/useTimer'

defineProps<{ elapsedHours: number }>()
</script>

<template>
  <div class="flex items-center gap-2 px-3 py-2 rounded-xl" :style="{ backgroundColor: getPhase(elapsedHours).color + '15' }">
    <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: getPhase(elapsedHours).color }"></div>
    <div>
      <div class="font-semibold text-sm" :style="{ color: getPhase(elapsedHours).color }">{{ getPhase(elapsedHours).name }}</div>
      <div class="text-xs" :style="{ color: 'var(--text-secondary)' }">{{ getPhase(elapsedHours).description }}</div>
    </div>
  </div>
</template>
