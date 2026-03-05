"""
Food router — search, log, and daily-summary endpoints.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import cast, Date, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FoodLog, User
from ..routers.auth import get_current_user
from ..schemas import DailySummary, FoodLogCreate, FoodLogOut, FoodSearchResult
from ..services.food_api import search_foods

router = APIRouter(prefix="/foods", tags=["foods"])


# ── GET /foods/search?q=… ─────────────────────────────────────

@router.get("/search", response_model=list[FoodSearchResult])
def food_search(
    q: str = Query(..., min_length=1, description="Food search term"),
    current_user: User = Depends(get_current_user),
):
    """Search the USDA FoodData Central API for foods matching *q*."""
    try:
        results = search_foods(q)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"USDA API error: {exc}",
        )
    return results


# ── POST /foods/log ────────────────────────────────────────────

@router.post("/log", response_model=FoodLogOut, status_code=status.HTTP_201_CREATED)
def log_food(
    entry: FoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Log a food item for the authenticated user.

    Macro values in the request body are **per 100 g**.
    The backend scales them by ``grams / 100``.
    """
    scale = entry.grams / 100.0
    log = FoodLog(
        user_id=current_user.id,
        food_name=entry.food_name,
        grams=round(entry.grams, 2),
        calories=round(entry.calories * scale, 2),
        protein=round(entry.protein * scale, 2),
        carbs=round(entry.carbs * scale, 2),
        fat=round(entry.fat * scale, 2),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ── GET /foods/today ───────────────────────────────────────────

@router.get("/today", response_model=DailySummary)
def daily_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregated macros for everything the user logged today."""
    today = date.today()
    row = (
        db.query(
            func.coalesce(func.sum(FoodLog.calories), 0),
            func.coalesce(func.sum(FoodLog.protein), 0),
            func.coalesce(func.sum(FoodLog.carbs), 0),
            func.coalesce(func.sum(FoodLog.fat), 0),
        )
        .filter(
            FoodLog.user_id == current_user.id,
            cast(FoodLog.created_at, Date) == today,
        )
        .first()
    )
    return {
        "calories": round(float(row[0]), 1),
        "protein": round(float(row[1]), 1),
        "carbs": round(float(row[2]), 1),
        "fat": round(float(row[3]), 1),
    }


# ── GET /foods/logs ────────────────────────────────────────────

@router.get("/logs", response_model=list[FoodLogOut])
def todays_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the individual food-log entries created today."""
    today = date.today()
    return (
        db.query(FoodLog)
        .filter(
            FoodLog.user_id == current_user.id,
            cast(FoodLog.created_at, Date) == today,
        )
        .order_by(FoodLog.created_at.desc())
        .all()
    )
