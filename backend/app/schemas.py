"""
Pydantic schemas for request / response validation.
"""

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
