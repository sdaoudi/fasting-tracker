from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
from typing import Optional

from database import get_db
from schemas import (
    FastCreate, FastUpdate, FastResponse,
    DailyLogCreate, DailyLogResponse,
    MealCreate, MealResponse,
    WeightCreate, WeightResponse, WeightTrend,
    StatsResponse, WeeklySummary,
)
import crud

app = FastAPI(title="Fasting Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://openclaw.host",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Fasts ──

@app.get("/api/fasts", response_model=list[FastResponse])
def list_fasts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud.get_fasts(db, skip=skip, limit=limit)


@app.get("/api/fasts/current", response_model=Optional[FastResponse])
def current_fast(db: Session = Depends(get_db)):
    return crud.get_current_fast(db)


@app.get("/api/fasts/{fast_id}", response_model=FastResponse)
def get_fast(fast_id: int, db: Session = Depends(get_db)):
    fast = crud.get_fast(db, fast_id)
    if not fast:
        raise HTTPException(status_code=404, detail="Fast not found")
    return fast


@app.post("/api/fasts", response_model=FastResponse, status_code=201)
def create_fast(fast: FastCreate, db: Session = Depends(get_db)):
    return crud.create_fast(db, fast)


@app.put("/api/fasts/{fast_id}", response_model=FastResponse)
def update_fast(fast_id: int, fast_update: FastUpdate, db: Session = Depends(get_db)):
    fast = crud.update_fast(db, fast_id, fast_update)
    if not fast:
        raise HTTPException(status_code=404, detail="Fast not found")
    return fast


@app.delete("/api/fasts/{fast_id}")
def delete_fast(fast_id: int, db: Session = Depends(get_db)):
    if not crud.delete_fast(db, fast_id):
        raise HTTPException(status_code=404, detail="Fast not found")
    return {"detail": "Fast deleted"}


# ── Daily Logs ──

@app.get("/api/fasts/{fast_id}/logs", response_model=list[DailyLogResponse])
def get_logs(fast_id: int, db: Session = Depends(get_db)):
    fast = crud.get_fast(db, fast_id)
    if not fast:
        raise HTTPException(status_code=404, detail="Fast not found")
    return crud.get_logs_for_fast(db, fast_id)


@app.post("/api/fasts/{fast_id}/logs", response_model=DailyLogResponse, status_code=201)
def create_log(fast_id: int, log: DailyLogCreate, db: Session = Depends(get_db)):
    fast = crud.get_fast(db, fast_id)
    if not fast:
        raise HTTPException(status_code=404, detail="Fast not found")
    return crud.create_log(db, fast_id, log)


# ── Meals ──

@app.get("/api/fasts/{fast_id}/meals", response_model=list[MealResponse])
def get_meals(fast_id: int, db: Session = Depends(get_db)):
    fast = crud.get_fast(db, fast_id)
    if not fast:
        raise HTTPException(status_code=404, detail="Fast not found")
    return crud.get_meals_for_fast(db, fast_id)


@app.post("/api/fasts/{fast_id}/meals", response_model=MealResponse, status_code=201)
def create_meal(fast_id: int, meal: MealCreate, db: Session = Depends(get_db)):
    fast = crud.get_fast(db, fast_id)
    if not fast:
        raise HTTPException(status_code=404, detail="Fast not found")
    return crud.create_meal(db, fast_id, meal)


@app.get("/api/meals/recent", response_model=list[MealResponse])
def recent_meals(limit: int = 20, db: Session = Depends(get_db)):
    return crud.get_recent_meals(db, limit=limit)


# ── Weight ──

@app.get("/api/weight", response_model=list[WeightResponse])
def weight_history(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    return crud.get_weight_history(db, start_date=start_date, end_date=end_date)


@app.post("/api/weight", response_model=WeightResponse, status_code=201)
def log_weight(weight: WeightCreate, db: Session = Depends(get_db)):
    return crud.create_weight(db, weight)


@app.get("/api/weight/trend", response_model=list[WeightTrend])
def weight_trend(days: int = 90, db: Session = Depends(get_db)):
    entries = crud.get_weight_trend(db, days=days)
    return [WeightTrend(weigh_date=e.weigh_date, weight=e.weight) for e in entries]


# ── Stats ──

@app.get("/api/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)


@app.get("/api/stats/weekly", response_model=list[WeeklySummary])
def weekly_stats(weeks: int = 8, db: Session = Depends(get_db)):
    return crud.get_weekly_summary(db, weeks=weeks)
