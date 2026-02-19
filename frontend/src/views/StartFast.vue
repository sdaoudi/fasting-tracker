<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createFast } from '../api/client'
import { saveActiveFast } from '../composables/useOfflineStorage'

const router = useRouter()

const fastTypes = [
  { label: '16:8', hours: 16 },
  { label: '18:6', hours: 18 },
  { label: '20:4', hours: 20 },
  { label: 'OMAD', hours: 23 },
  { label: '48h', hours: 48 },
  { label: '72h', hours: 72 },
]

const selectedType = ref('48h')
const selectedHours = ref(48)
const customHours = ref(24)
const isCustom = ref(false)
const weightBefore = ref<string>('')
const notes = ref('')
const customStart = ref('')
const submitting = ref(false)

function selectType(type: { label: string; hours: number }) {
  selectedType.value = type.label
  selectedHours.value = type.hours
  isCustom.value = false
}

function selectCustom() {
  isCustom.value = true
  selectedType.value = 'Custom'
}

async function startFast() {
  submitting.value = true
  try {
    const data: Record<string, unknown> = {
      type: selectedType.value,
      target_hours: isCustom.value ? customHours.value : selectedHours.value,
    }
    if (weightBefore.value) data.weight_before = parseFloat(weightBefore.value)
    if (notes.value) data.notes = notes.value
    if (customStart.value) data.started = new Date(customStart.value).toISOString()

    const fast = await createFast(data as Parameters<typeof createFast>[0])
    saveActiveFast(fast)
    router.push(`/fast/${fast.id}`)
  } catch (e) {
    alert('Erreur: ' + (e as Error).message)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-lg mx-auto px-5 pt-6 pb-8">
    <h1 class="text-2xl font-bold mb-6">Démarrer un Jeûne</h1>

    <!-- Type selection -->
    <div class="mb-6">
      <label class="text-sm font-medium mb-2 block">Type de jeûne</label>
      <div class="grid grid-cols-3 gap-2">
        <button v-for="t in fastTypes" :key="t.label" @click="selectType(t)"
          class="py-3 rounded-xl font-semibold text-center cursor-pointer border-2 transition-all"
          :class="selectedType === t.label && !isCustom ? 'border-teal-primary bg-teal-primary/10 text-teal-primary' : ''"
          :style="selectedType !== t.label || isCustom ? { backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' } : {}">
          {{ t.label }}
        </button>
        <button @click="selectCustom"
          class="py-3 rounded-xl font-semibold text-center cursor-pointer border-2 transition-all col-span-3"
          :class="isCustom ? 'border-teal-primary bg-teal-primary/10 text-teal-primary' : ''"
          :style="!isCustom ? { backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' } : {}">
          Personnalisé
        </button>
      </div>
    </div>

    <!-- Custom hours -->
    <div v-if="isCustom" class="mb-6">
      <label class="text-sm font-medium mb-2 block">Durée (heures)</label>
      <input v-model.number="customHours" type="number" min="1" max="168"
        class="w-full px-4 py-2.5 rounded-xl border outline-none"
        :style="{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }" />
    </div>

    <!-- Weight before -->
    <div class="mb-6">
      <label class="text-sm font-medium mb-2 block">Poids avant (optionnel)</label>
      <input v-model="weightBefore" type="number" step="0.1" placeholder="ex: 85.5"
        class="w-full px-4 py-2.5 rounded-xl border outline-none"
        :style="{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }" />
    </div>

    <!-- Notes -->
    <div class="mb-6">
      <label class="text-sm font-medium mb-2 block">Notes (optionnel)</label>
      <textarea v-model="notes" rows="3" placeholder="Objectif, motivation..."
        class="w-full px-4 py-2.5 rounded-xl border outline-none resize-none"
        :style="{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }"></textarea>
    </div>

    <!-- Custom start time -->
    <div class="mb-6">
      <label class="text-sm font-medium mb-2 block">Heure de début (optionnel, défaut : maintenant)</label>
      <input v-model="customStart" type="datetime-local"
        class="w-full px-4 py-2.5 rounded-xl border outline-none appearance-none min-h-[44px]"
        :style="{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)', colorScheme: 'light dark', WebkitTextFillColor: 'var(--text-primary)' }" />
    </div>

    <!-- Submit -->
    <button @click="startFast" :disabled="submitting"
      class="w-full py-3 rounded-xl font-bold text-lg text-white bg-teal-primary disabled:opacity-50 border-0 cursor-pointer">
      {{ submitting ? 'Démarrage...' : 'Démarrer le Jeûne' }}
    </button>
  </div>
</template>
