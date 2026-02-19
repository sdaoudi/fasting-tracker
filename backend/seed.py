"""
Seed script — runs automatically on startup if meal_recommendations is empty.
"""
import json
import os

from sqlalchemy.orm import Session
from database import engine, Base
import models


def seed_meal_recommendations(db: Session):
    count = db.query(models.MealRecommendation).count()
    if count > 0:
        return  # already seeded

    seed_file = os.path.join(os.path.dirname(__file__), "seed_meals.json")
    with open(seed_file, "r", encoding="utf-8") as f:
        meals = json.load(f)

    for m in meals:
        db.add(models.MealRecommendation(
            name=m["name"],
            category=m["category"],
            fast_duration=m.get("fast_duration"),
            phase=m.get("phase"),
            description=m.get("description"),
            ingredients=m.get("ingredients"),
            macros=m.get("macros"),
            preparation_time=m.get("preparation_time"),
            difficulty=m.get("difficulty"),
            tips=m.get("tips"),
            digestibility=m.get("digestibility"),
            meal_timing=m.get("meal_timing"),
        ))

    db.commit()
    print(f"[seed] {len(meals)} meal recommendations inserted.")


def run():
    Base.metadata.create_all(bind=engine)
    from database import SessionLocal
    db = SessionLocal()
    try:
        seed_meal_recommendations(db)
    finally:
        db.close()
