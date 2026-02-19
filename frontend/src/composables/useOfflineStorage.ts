import type { Fast } from '../types'

const ACTIVE_FAST_KEY = 'fasting_active_fast'

export function saveActiveFast(fast: Fast) {
  localStorage.setItem(ACTIVE_FAST_KEY, JSON.stringify(fast))
}

export function loadActiveFast(): Fast | null {
  const raw = localStorage.getItem(ACTIVE_FAST_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as Fast
  } catch {
    return null
  }
}

export function clearActiveFast() {
  localStorage.removeItem(ACTIVE_FAST_KEY)
}
