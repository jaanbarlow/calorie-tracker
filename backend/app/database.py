"""
Database engine and session configuration.

Reads DATABASE_URL from the environment and exposes:
  - engine          – SQLAlchemy engine instance
  - SessionLocal    – scoped session factory
  - Base            – declarative base for ORM models
  - get_db()        – FastAPI dependency that yields a DB session
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgres:5432/calorietracker",
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency – yields a SQLAlchemy session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
