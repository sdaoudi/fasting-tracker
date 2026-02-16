from sqlalchemy import (
    Column, Integer, String, Boolean, Text, Numeric, Date, DateTime, ARRAY,
    ForeignKey, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Fast(Base):
    __tablename__ = "fasts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False, default="48h")
    started = Column(DateTime(timezone=True), nullable=False)
    ended = Column(DateTime(timezone=True), nullable=True)
    target_hours = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    weight_before = Column(Numeric(5, 1), nullable=True)
    weight_after = Column(Numeric(5, 1), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    logs = relationship("DailyLog", back_populates="fast", cascade="all, delete-orphan")
    meals = relationship("Meal", back_populates="fast", cascade="all, delete-orphan")


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    fast_id = Column(Integer, ForeignKey("fasts.id"), nullable=True)
    log_date = Column(Date, nullable=False)
    water_liters = Column(Numeric(3, 1), nullable=True)
    electrolytes = Column(Boolean, default=False)
    energy_level = Column(Integer, nullable=True)
    hunger_level = Column(Integer, nullable=True)
    mood = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    fast = relationship("Fast", back_populates="logs")

    __table_args__ = (
        CheckConstraint("energy_level BETWEEN 1 AND 10", name="ck_energy_level"),
        CheckConstraint("hunger_level BETWEEN 1 AND 10", name="ck_hunger_level"),
    )


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    fast_id = Column(Integer, ForeignKey("fasts.id"), nullable=True)
    meal_type = Column(String(20), nullable=False)
    meal_name = Column(String(100), nullable=True)
    ingredients = Column(ARRAY(Text), nullable=True)
    calories = Column(Integer, nullable=True)
    meal_time = Column(DateTime(timezone=True), nullable=True)
    is_breaking_fast = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    fast = relationship("Fast", back_populates="meals")


class MealRecommendation(Base):
    __tablename__ = "meal_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    fast_duration = Column(String(20), nullable=True)
    phase = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    ingredients = Column(ARRAY(Text), nullable=True)
    macros = Column(JSONB, nullable=True)
    preparation_time = Column(Integer, nullable=True)
    difficulty = Column(String(20), nullable=True)
    tips = Column(Text, nullable=True)
    digestibility = Column(String(20), nullable=True)
    meal_timing = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class WeightLog(Base):
    __tablename__ = "weight_log"

    id = Column(Integer, primary_key=True, index=True)
    weigh_date = Column(Date, nullable=False, unique=True)
    weight = Column(Numeric(5, 1), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
