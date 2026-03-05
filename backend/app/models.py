"""
SQLAlchemy ORM models.
"""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    # Body metrics (nullable – filled in later by the user)
    weight = Column(Float, nullable=True)       # kg
    height = Column(Float, nullable=True)       # cm
    age = Column(Integer, nullable=True)

    # "sedentary" | "light" | "moderate" | "active" | "very_active"
    activity_level = Column(String, nullable=True)

    # "lose" | "maintain" | "gain"
    goal_type = Column(String, nullable=True)


class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    food_name = Column(String, nullable=False)
    grams = Column(Float, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
