<script setup lang="ts">
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="min-h-screen lg:pb-0 lg:pl-56" style="background-color: var(--bg-primary); color: var(--text-primary); padding-bottom: max(5rem, calc(4rem + env(safe-area-inset-bottom)));">
    <router-view />
    <NavBar />
  </div>
</template>
