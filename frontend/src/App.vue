<script setup lang="ts">
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="min-h-screen pb-20 lg:pb-0 lg:pl-56" style="background-color: var(--bg-primary); color: var(--text-primary);">
    <router-view />
    <NavBar />
  </div>
</template>
