export interface Fast {
  id: number
  type: string
  started: string
  ended: string | null
  target_hours: number
  completed: boolean
  notes: string | null
  weight_before: number | null
  weight_after: number | null
  created_at: string
  updated_at: string
}

export interface DailyLog {
  id: number
  fast_id: number
  log_date: string
  water_liters: number | null
  electrolytes: boolean
  energy_level: number | null
  hunger_level: number | null
  mood: string | null
  notes: string | null
  created_at: string
}

export interface Meal {
  id: number
  fast_id: number | null
  meal_type: string
  meal_name: string | null
  ingredients: string[] | null
  calories: number | null
  meal_time: string | null
  is_breaking_fast: boolean
  notes: string | null
  created_at: string
}

export interface WeightEntry {
  id: number
  weigh_date: string
  weight: number
  notes: string | null
  created_at: string
}

export interface WeightTrend {
  weigh_date: string
  weight: number
}

export interface Stats {
  total_fasts: number
  completed_fasts: number
  avg_duration_hours: number | null
  total_weight_lost: number | null
  by_type: Record<string, number>
}

export interface WeeklySummary {
  week_start: string
  fasts_started: number
  fasts_completed: number
  avg_duration_hours: number | null
  weight_change: number | null
}
