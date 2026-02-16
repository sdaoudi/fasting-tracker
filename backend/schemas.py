from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


# --- Fasts ---

class FastCreate(BaseModel):
    type: str = "48h"
    target_hours: int = 48
    started: Optional[datetime] = None
    notes: Optional[str] = None
    weight_before: Optional[Decimal] = None


class FastUpdate(BaseModel):
    ended: Optional[datetime] = None
    completed: Optional[bool] = None
    notes: Optional[str] = None
    weight_before: Optional[Decimal] = None
    weight_after: Optional[Decimal] = None


class FastResponse(BaseModel):
    id: int
    type: str
    started: datetime
    ended: Optional[datetime]
    target_hours: int
    completed: bool
    notes: Optional[str]
    weight_before: Optional[Decimal]
    weight_after: Optional[Decimal]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# --- Daily Logs ---

class DailyLogCreate(BaseModel):
    log_date: Optional[date] = None
    water_liters: Optional[Decimal] = None
    electrolytes: Optional[bool] = False
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    hunger_level: Optional[int] = Field(None, ge=1, le=10)
    mood: Optional[str] = None
    notes: Optional[str] = None


class DailyLogResponse(BaseModel):
    id: int
    fast_id: Optional[int]
    log_date: date
    water_liters: Optional[Decimal]
    electrolytes: bool
    energy_level: Optional[int]
    hunger_level: Optional[int]
    mood: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


# --- Meals ---

class MealCreate(BaseModel):
    meal_type: str
    meal_name: Optional[str] = None
    ingredients: Optional[list[str]] = None
    calories: Optional[int] = None
    meal_time: Optional[datetime] = None
    is_breaking_fast: Optional[bool] = False
    notes: Optional[str] = None


class MealResponse(BaseModel):
    id: int
    fast_id: Optional[int]
    meal_type: str
    meal_name: Optional[str]
    ingredients: Optional[list[str]]
    calories: Optional[int]
    meal_time: Optional[datetime]
    is_breaking_fast: bool
    notes: Optional[str]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


# --- Weight ---

class WeightCreate(BaseModel):
    weigh_date: Optional[date] = None
    weight: Decimal
    notes: Optional[str] = None


class WeightResponse(BaseModel):
    id: int
    weigh_date: date
    weight: Decimal
    notes: Optional[str]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class WeightTrend(BaseModel):
    weigh_date: date
    weight: Decimal


# --- Stats ---

class StatsResponse(BaseModel):
    total_fasts: int
    completed_fasts: int
    avg_duration_hours: Optional[float]
    total_weight_lost: Optional[float]
    by_type: dict[str, int]


class WeeklySummary(BaseModel):
    week_start: date
    fasts_started: int
    fasts_completed: int
    avg_duration_hours: Optional[float]
    weight_change: Optional[float]


# --- Meal Recommendations ---

class Macros(BaseModel):
    calories: Optional[int] = None
    protein: Optional[int] = None
    carbs: Optional[int] = None
    fat: Optional[int] = None


class MealRecommendationResponse(BaseModel):
    id: int
    name: str
    category: str
    fast_duration: Optional[str]
    phase: Optional[str]
    description: Optional[str]
    ingredients: Optional[list[str]]
    macros: Optional[Macros]
    preparation_time: Optional[int]
    difficulty: Optional[str]
    tips: Optional[str]
    digestibility: Optional[str]
    meal_timing: Optional[str]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class MealRecommendationSuggestParams(BaseModel):
    fast_id: Optional[int] = None
    fast_duration: Optional[str] = None
    phase: Optional[str] = None
    meal_timing: Optional[str] = None


class CategoryCount(BaseModel):
    category: str
    count: int
