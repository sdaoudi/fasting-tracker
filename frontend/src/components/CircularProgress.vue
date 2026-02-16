<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  progress: number
  size?: number
  strokeWidth?: number
  color?: string
}>()

const size = computed(() => props.size ?? 200)
const stroke = computed(() => props.strokeWidth ?? 12)
const radius = computed(() => (size.value - stroke.value) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const offset = computed(() => circumference.value * (1 - Math.min(1, props.progress)))
const color = computed(() => props.color ?? '#0d9488')
</script>

<template>
  <div class="relative inline-flex items-center justify-center" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" class="rotate-[-90deg]">
      <circle :cx="size / 2" :cy="size / 2" :r="radius" fill="none"
        stroke="var(--border-color)" :stroke-width="stroke" />
      <circle :cx="size / 2" :cy="size / 2" :r="radius" fill="none"
        :stroke="color" :stroke-width="stroke" stroke-linecap="round"
        :stroke-dasharray="circumference" :stroke-dashoffset="offset"
        class="transition-[stroke-dashoffset] duration-1000 ease-out" />
    </svg>
    <div class="absolute inset-0 flex items-center justify-center">
      <slot />
    </div>
  </div>
</template>
