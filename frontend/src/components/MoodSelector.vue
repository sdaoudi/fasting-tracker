<script setup lang="ts">
const model = defineModel<string>()

const moods = [
  { emoji: '\u{1F60A}', value: 'happy' },
  { emoji: '\u{1F610}', value: 'neutral' },
  { emoji: '\u{1F623}', value: 'struggling' },
  { emoji: '\u{1F922}', value: 'nauseous' },
  { emoji: '\u{1F634}', value: 'tired' },
  { emoji: '\u{1F4AA}', value: 'strong' },
]
</script>

<template>
  <div class="flex gap-2">
    <button v-for="m in moods" :key="m.value" @click="model = m.value"
      class="w-10 h-10 rounded-xl text-xl flex items-center justify-center cursor-pointer border-2 transition-all"
      :class="model === m.value ? 'border-teal-primary scale-110' : 'border-transparent'"
      :style="{ backgroundColor: model === m.value ? 'var(--bg-primary)' : 'transparent' }">
      {{ m.emoji }}
    </button>
  </div>
</template>
