from sqlalchemy.orm import Session
from sqlalchemy import desc, func, extract
from datetime import datetime, date, timedelta, timezone
from typing import Optional
from decimal import Decimal

import models
import schemas


# ── Fasts ──

def get_fasts(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.Fast).order_by(desc(models.Fast.started)).offset(skip).limit(limit).all()


def get_fast(db: Session, fast_id: int):
    return db.query(models.Fast).filter(models.Fast.id == fast_id).first()


def get_current_fast(db: Session):
    return db.query(models.Fast).filter(
        models.Fast.ended.is_(None),
        models.Fast.completed.is_(False)
    ).order_by(desc(models.Fast.started)).first()


def create_fast(db: Session, fast: schemas.FastCreate):
    db_fast = models.Fast(
        type=fast.type,
        target_hours=fast.target_hours,
        started=fast.started or datetime.now(timezone.utc),
        notes=fast.notes,
        weight_before=fast.weight_before,
    )
    db.add(db_fast)
    db.commit()
    db.refresh(db_fast)
    return db_fast


def update_fast(db: Session, fast_id: int, fast_update: schemas.FastUpdate):
    db_fast = db.query(models.Fast).filter(models.Fast.id == fast_id).first()
    if not db_fast:
        return None
    update_data = fast_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_fast, key, value)
    db_fast.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_fast)
    return db_fast


def delete_fast(db: Session, fast_id: int):
    db_fast = db.query(models.Fast).filter(models.Fast.id == fast_id).first()
    if not db_fast:
        return False
    db.delete(db_fast)
    db.commit()
    return True


# ── Daily Logs ──

def get_logs_for_fast(db: Session, fast_id: int):
    return db.query(models.DailyLog).filter(
        models.DailyLog.fast_id == fast_id
    ).order_by(desc(models.DailyLog.log_date)).all()


def create_log(db: Session, fast_id: int, log: schemas.DailyLogCreate):
    db_log = models.DailyLog(
        fast_id=fast_id,
        log_date=log.log_date or date.today(),
        water_liters=log.water_liters,
        electrolytes=log.electrolytes,
        energy_level=log.energy_level,
        hunger_level=log.hunger_level,
        mood=log.mood,
        notes=log.notes,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


# ── Meals ──

def get_meals_for_fast(db: Session, fast_id: int):
    return db.query(models.Meal).filter(
        models.Meal.fast_id == fast_id
    ).order_by(desc(models.Meal.meal_time)).all()


def create_meal(db: Session, fast_id: int, meal: schemas.MealCreate):
    db_meal = models.Meal(
        fast_id=fast_id,
        meal_type=meal.meal_type,
        meal_name=meal.meal_name,
        ingredients=meal.ingredients,
        calories=meal.calories,
        meal_time=meal.meal_time or datetime.now(timezone.utc),
        is_breaking_fast=meal.is_breaking_fast,
        notes=meal.notes,
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def get_recent_meals(db: Session, limit: int = 20):
    return db.query(models.Meal).order_by(desc(models.Meal.created_at)).limit(limit).all()


# ── Weight ──

def get_weight_history(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None):
    q = db.query(models.WeightLog)
    if start_date:
        q = q.filter(models.WeightLog.weigh_date >= start_date)
    if end_date:
        q = q.filter(models.WeightLog.weigh_date <= end_date)
    return q.order_by(desc(models.WeightLog.weigh_date)).all()


def create_weight(db: Session, weight: schemas.WeightCreate):
    weigh_date = weight.weigh_date or date.today()
    existing = db.query(models.WeightLog).filter(
        models.WeightLog.weigh_date == weigh_date
    ).first()
    if existing:
        existing.weight = weight.weight
        existing.notes = weight.notes
        db.commit()
        db.refresh(existing)
        return existing
    db_weight = models.WeightLog(
        weigh_date=weigh_date,
        weight=weight.weight,
        notes=weight.notes,
    )
    db.add(db_weight)
    db.commit()
    db.refresh(db_weight)
    return db_weight


def get_weight_trend(db: Session, days: int = 90):
    since = date.today() - timedelta(days=days)
    return db.query(models.WeightLog).filter(
        models.WeightLog.weigh_date >= since
    ).order_by(models.WeightLog.weigh_date).all()


# ── Stats ──

def get_stats(db: Session):
    total = db.query(func.count(models.Fast.id)).scalar() or 0
    completed = db.query(func.count(models.Fast.id)).filter(models.Fast.completed.is_(True)).scalar() or 0

    # Average duration for completed fasts
    completed_fasts = db.query(models.Fast).filter(
        models.Fast.completed.is_(True),
        models.Fast.ended.isnot(None)
    ).all()
    avg_hours = None
    if completed_fasts:
        durations = [(f.ended - f.started).total_seconds() / 3600 for f in completed_fasts]
        avg_hours = round(sum(durations) / len(durations), 1)

    # Total weight lost (first weight log entry - last weight log entry)
    total_lost = None
    first_weight = db.query(models.WeightLog).order_by(models.WeightLog.weigh_date).first()
    last_weight = db.query(models.WeightLog).order_by(desc(models.WeightLog.weigh_date)).first()
    if first_weight and last_weight and first_weight.id != last_weight.id:
        total_lost = float(first_weight.weight - last_weight.weight)

    # By type
    type_counts = db.query(
        models.Fast.type, func.count(models.Fast.id)
    ).group_by(models.Fast.type).all()
    by_type = {t: c for t, c in type_counts}

    return schemas.StatsResponse(
        total_fasts=total,
        completed_fasts=completed,
        avg_duration_hours=avg_hours,
        total_weight_lost=total_lost,
        by_type=by_type,
    )


# ── Meal Recommendations ──

DIGESTIBILITY_ORDER = {"très_facile": 0, "facile": 1, "moyen": 2}


def get_meal_recommendation(db: Session, rec_id: int):
    return db.query(models.MealRecommendation).filter(
        models.MealRecommendation.id == rec_id
    ).first()


def get_meal_recommendation_categories(db: Session):
    results = db.query(
        models.MealRecommendation.category,
        func.count(models.MealRecommendation.id)
    ).group_by(models.MealRecommendation.category).all()
    return [{"category": cat, "count": cnt} for cat, cnt in results]


def get_meal_suggestions(
    db: Session,
    fast_id: Optional[int] = None,
    fast_duration: Optional[str] = None,
    phase: Optional[str] = None,
    meal_timing: Optional[str] = None,
    limit: int = 50,
):
    q = db.query(models.MealRecommendation)

    # If we have a fast_id, derive context from the actual fast
    resolved_duration = fast_duration
    if fast_id and not fast_duration:
        fast = db.query(models.Fast).filter(models.Fast.id == fast_id).first()
        if fast:
            resolved_duration = fast.type

    # Apply smart filtering based on fast duration
    if resolved_duration:
        duration_hours = _parse_duration_hours(resolved_duration)
        if duration_hours is not None:
            if duration_hours < 24:
                q = q.filter(
                    models.MealRecommendation.category.in_(["rupture_jeune", "repas_fenetre"])
                )
            elif duration_hours <= 48:
                q = q.filter(
                    models.MealRecommendation.category == "rupture_jeune",
                    models.MealRecommendation.digestibility.in_(["très_facile", "facile"])
                )
            elif duration_hours <= 72:
                q = q.filter(
                    models.MealRecommendation.category == "reprise_progressive"
                )
                if not phase:
                    q = q.filter(
                        models.MealRecommendation.phase.in_(["jour_1", "jour_2", "jour_3"])
                    )
            else:
                q = q.filter(
                    models.MealRecommendation.category == "reprise_progressive",
                    models.MealRecommendation.fast_duration == "7j+"
                )
        else:
            # Match exact fast_duration string (e.g. "7j+")
            q = q.filter(models.MealRecommendation.fast_duration == resolved_duration)

    if phase:
        q = q.filter(models.MealRecommendation.phase == phase)

    if meal_timing:
        q = q.filter(models.MealRecommendation.meal_timing == meal_timing)

    results = q.all()

    # Sort by digestibility (easiest first), then by preparation_time (fastest first)
    results.sort(key=lambda r: (
        DIGESTIBILITY_ORDER.get(r.digestibility, 99),
        r.preparation_time or 999,
    ))

    return results[:limit]


def _parse_duration_hours(duration_str: str) -> Optional[int]:
    """Parse a fast duration string like '48h', '16:8', 'OMAD', '7j+' into hours."""
    d = duration_str.strip().lower()
    if d.endswith("h") and d[:-1].isdigit():
        return int(d[:-1])
    mapping = {
        "16:8": 16, "18:6": 18, "20:4": 20,
        "omad": 23, "7j+": 168,
    }
    return mapping.get(d)


def get_weekly_summary(db: Session, weeks: int = 8):
    results = []
    today = date.today()
    for i in range(weeks):
        week_end = today - timedelta(days=i * 7)
        week_start = week_end - timedelta(days=6)

        started = db.query(func.count(models.Fast.id)).filter(
            func.date(models.Fast.started) >= week_start,
            func.date(models.Fast.started) <= week_end
        ).scalar() or 0

        completed_count = db.query(func.count(models.Fast.id)).filter(
            models.Fast.completed.is_(True),
            func.date(models.Fast.ended) >= week_start,
            func.date(models.Fast.ended) <= week_end
        ).scalar() or 0

        # Weight change in that week
        w_start = db.query(models.WeightLog).filter(
            models.WeightLog.weigh_date >= week_start,
            models.WeightLog.weigh_date <= week_end
        ).order_by(models.WeightLog.weigh_date).first()

        w_end = db.query(models.WeightLog).filter(
            models.WeightLog.weigh_date >= week_start,
            models.WeightLog.weigh_date <= week_end
        ).order_by(desc(models.WeightLog.weigh_date)).first()

        weight_change = None
        if w_start and w_end and w_start.id != w_end.id:
            weight_change = float(w_end.weight - w_start.weight)

        results.append(schemas.WeeklySummary(
            week_start=week_start,
            fasts_started=started,
            fasts_completed=completed_count,
            avg_duration_hours=None,
            weight_change=weight_change,
        ))

    return results
