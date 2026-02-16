const BASE_URL = import.meta.env.PROD
  ? ''
  : 'http://localhost:8042'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`${res.status}: ${detail}`)
  }
  if (res.status === 204) return null as T
  return res.json()
}

import type { Fast, DailyLog, Meal, WeightEntry, WeightTrend, Stats, WeeklySummary } from '../types'

// Fasts
export const getFasts = (skip = 0, limit = 20) =>
  request<Fast[]>(`/api/fasts?skip=${skip}&limit=${limit}`)

export const getCurrentFast = () =>
  request<Fast | null>('/api/fasts/current')

export const getFast = (id: number) =>
  request<Fast>(`/api/fasts/${id}`)

export const createFast = (data: {
  type: string; target_hours: number; started?: string; notes?: string; weight_before?: number
}) => request<Fast>('/api/fasts', { method: 'POST', body: JSON.stringify(data) })

export const updateFast = (id: number, data: Record<string, unknown>) =>
  request<Fast>(`/api/fasts/${id}`, { method: 'PUT', body: JSON.stringify(data) })

export const deleteFast = (id: number) =>
  request<void>(`/api/fasts/${id}`, { method: 'DELETE' })

// Daily Logs
export const getLogs = (fastId: number) =>
  request<DailyLog[]>(`/api/fasts/${fastId}/logs`)

export const createLog = (fastId: number, data: Record<string, unknown>) =>
  request<DailyLog>(`/api/fasts/${fastId}/logs`, { method: 'POST', body: JSON.stringify(data) })

// Meals
export const getMeals = (fastId: number) =>
  request<Meal[]>(`/api/fasts/${fastId}/meals`)

export const createMeal = (fastId: number, data: Record<string, unknown>) =>
  request<Meal>(`/api/fasts/${fastId}/meals`, { method: 'POST', body: JSON.stringify(data) })

export const getRecentMeals = (limit = 20) =>
  request<Meal[]>(`/api/meals/recent?limit=${limit}`)

// Weight
export const getWeightHistory = (startDate?: string, endDate?: string) => {
  const params = new URLSearchParams()
  if (startDate) params.set('start_date', startDate)
  if (endDate) params.set('end_date', endDate)
  const qs = params.toString()
  return request<WeightEntry[]>(`/api/weight${qs ? '?' + qs : ''}`)
}

export const logWeight = (data: { weight: number; weigh_date?: string; notes?: string }) =>
  request<WeightEntry>('/api/weight', { method: 'POST', body: JSON.stringify(data) })

export const getWeightTrend = (days = 90) =>
  request<WeightTrend[]>(`/api/weight/trend?days=${days}`)

// Stats
export const getStats = () =>
  request<Stats>('/api/stats')

export const getWeeklyStats = (weeks = 8) =>
  request<WeeklySummary[]>(`/api/stats/weekly?weeks=${weeks}`)
