"""
SQLAlchemy ORM models.
"""

from sqlalchemy import Column, Float, Integer, String

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
