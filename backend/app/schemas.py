"""
Pydantic schemas for request / response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ── Auth requests ──────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None
    activity_level: Optional[str] = None
    goal_type: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ── Auth responses ─────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None
    activity_level: Optional[str] = None
    goal_type: Optional[str] = None

    class Config:
        from_attributes = True


# ── Food search ────────────────────────────────────────────────

class FoodSearchResult(BaseModel):
    fdc_id: int
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float


# ── Food logging ───────────────────────────────────────────────

class FoodLogCreate(BaseModel):
    food_name: str
    grams: float
    calories: float
    protein: float
    carbs: float
    fat: float


class FoodLogOut(BaseModel):
    id: int
    food_name: str
    grams: float
    calories: float
    protein: float
    carbs: float
    fat: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── Daily summary ──────────────────────────────────────────────

class DailySummary(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
