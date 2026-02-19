<script setup lang="ts">
import NavBar from './components/NavBar.vue'
import { useOnlineStatus } from './composables/useOnlineStatus'

const { isOnline } = useOnlineStatus()
</script>

<template>
  <div class="min-h-screen lg:pb-0 lg:pl-56" style="background-color: var(--bg-primary); color: var(--text-primary); padding-bottom: max(5rem, calc(4rem + env(safe-area-inset-bottom)));">
    <!-- Offline banner -->
    <Transition name="offline-banner">
      <div v-if="!isOnline" class="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 py-1.5 text-xs font-medium text-white"
        style="background-color: #f59e0b;">
        <span style="font-size: 10px;">&#9679;</span>
        Hors ligne — le chrono continue
      </div>
    </Transition>
    <div :style="{ paddingTop: isOnline ? '0' : '28px', transition: 'padding-top 0.3s ease' }">
      <router-view />
    </div>
    <NavBar />
  </div>
</template>

<style scoped>
.offline-banner-enter-active,
.offline-banner-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.offline-banner-enter-from,
.offline-banner-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
