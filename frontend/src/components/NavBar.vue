<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useDark } from '../composables/useDark'

const route = useRoute()
const { isDark, toggle } = useDark()

const tabs = [
  { path: '/', icon: '\u{1F3E0}', label: 'Accueil' },
  { path: '/start', icon: '\u23F1\uFE0F', label: 'Jeûne' },
  { path: '/stats', icon: '\u{1F4CA}', label: 'Stats' },
  { path: '/weight', icon: '\u2696\uFE0F', label: 'Poids' },
  { path: '/meals', icon: '\u{1F4DD}', label: 'Repas' },
]
</script>

<template>
  <!-- Mobile bottom bar -->
  <nav class="fixed bottom-0 left-0 right-0 lg:hidden flex justify-around items-center h-16 border-t z-50"
    :style="{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)' }">
    <router-link v-for="tab in tabs" :key="tab.path" :to="tab.path"
      class="flex flex-col items-center gap-0.5 text-xs no-underline transition-colors"
      :class="route.path === tab.path ? 'text-teal-primary font-bold' : ''"
      :style="route.path === tab.path ? {} : { color: 'var(--text-secondary)' }">
      <span class="text-xl">{{ tab.icon }}</span>
      <span>{{ tab.label }}</span>
    </router-link>
  </nav>

  <!-- Desktop sidebar -->
  <aside class="hidden lg:flex fixed left-0 top-0 bottom-0 w-56 flex-col border-r z-50 p-4"
    :style="{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)' }">
    <div class="text-xl font-bold text-teal-primary mb-8">Fasting Tracker</div>
    <router-link v-for="tab in tabs" :key="tab.path" :to="tab.path"
      class="flex items-center gap-3 px-3 py-2.5 rounded-xl mb-1 no-underline transition-colors"
      :class="route.path === tab.path ? 'bg-teal-primary/10 text-teal-primary font-semibold' : ''"
      :style="route.path === tab.path ? {} : { color: 'var(--text-secondary)' }">
      <span class="text-lg">{{ tab.icon }}</span>
      <span>{{ tab.label }}</span>
    </router-link>
    <router-link to="/history"
      class="flex items-center gap-3 px-3 py-2.5 rounded-xl mb-1 no-underline transition-colors"
      :class="route.path === '/history' ? 'bg-teal-primary/10 text-teal-primary font-semibold' : ''"
      :style="route.path === '/history' ? {} : { color: 'var(--text-secondary)' }">
      <span class="text-lg">{{'📋'}}</span>
      <span>Historique</span>
    </router-link>
    <div class="mt-auto">
      <button @click="toggle" class="flex items-center gap-2 px-3 py-2 rounded-xl w-full text-left border-0 cursor-pointer"
        :style="{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-secondary)' }">
        <span>{{ isDark ? '\u2600\uFE0F' : '\u{1F319}' }}</span>
        <span class="text-sm">{{ isDark ? 'Mode clair' : 'Mode sombre' }}</span>
      </button>
    </div>
  </aside>
</template>
