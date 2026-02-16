<script setup lang="ts">
const model = defineModel<number>()

defineProps<{
  min?: number
  max?: number
  step?: number
  label: string
  unit?: string
}>()
</script>

<template>
  <div>
    <div class="flex justify-between mb-1">
      <span class="text-sm font-medium">{{ label }}</span>
      <span class="text-sm font-bold text-teal-primary">{{ model ?? '-' }}{{ unit ?? '' }}</span>
    </div>
    <input type="range" :min="min ?? 0" :max="max ?? 10" :step="step ?? 1" :value="model ?? 0"
      @input="model = Number(($event.target as HTMLInputElement).value)"
      class="w-full h-2 rounded-lg appearance-none cursor-pointer accent-teal-primary"
      :style="{ backgroundColor: 'var(--border-color)' }" />
  </div>
</template>
