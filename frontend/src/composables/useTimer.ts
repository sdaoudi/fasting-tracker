import { ref, computed, onUnmounted } from 'vue'

export function useTimer(startedAt: string, targetHours: number) {
  const now = ref(Date.now())
  let interval: ReturnType<typeof setInterval> | null = null

  const startMs = new Date(startedAt).getTime()
  const targetMs = targetHours * 3600 * 1000

  const elapsed = computed(() => Math.max(0, now.value - startMs))
  const remaining = computed(() => Math.max(0, targetMs - elapsed.value))
  const progress = computed(() => Math.min(1, elapsed.value / targetMs))
  const isOvertime = computed(() => elapsed.value > targetMs)

  const elapsedFormatted = computed(() => formatDuration(elapsed.value))
  const remainingFormatted = computed(() => formatDuration(remaining.value))

  function start() {
    if (interval) return
    interval = setInterval(() => { now.value = Date.now() }, 1000)
  }

  function stop() {
    if (interval) {
      clearInterval(interval)
      interval = null
    }
  }

  start()
  onUnmounted(stop)

  return { elapsed, remaining, progress, isOvertime, elapsedFormatted, remainingFormatted, start, stop }
}

export function formatDuration(ms: number): string {
  const totalSec = Math.floor(ms / 1000)
  const h = Math.floor(totalSec / 3600)
  const m = Math.floor((totalSec % 3600) / 60)
  const s = totalSec % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

export function getPhase(elapsedHours: number) {
  if (elapsedHours < 12) return { name: 'Facile', color: '#10b981', description: 'Phase initiale - le corps utilise le glycogene' }
  if (elapsedHours < 24) return { name: 'Transition Cetose', color: '#f59e0b', description: 'Transition vers la cetose - le corps commence a bruler les graisses' }
  if (elapsedHours < 36) return { name: 'Difficile', color: '#ef4444', description: 'Phase difficile - adaptation metabolique' }
  return { name: 'Stabilisation', color: '#8b5cf6', description: 'Cetose profonde - le corps est adapte' }
}
