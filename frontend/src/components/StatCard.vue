<script setup lang="ts">
defineProps<{
  icon: string
  label: string
  value: string | number
}>()
</script>

<template>
  <div class="rounded-2xl p-4 shadow-sm" :style="{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }">
    <div class="text-2xl mb-1">{{ icon }}</div>
    <div class="text-xl font-bold">{{ value }}</div>
    <div class="text-sm" :style="{ color: 'var(--text-secondary)' }">{{ label }}</div>
  </div>
</template>
