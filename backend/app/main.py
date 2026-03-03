"""
Calorie & Macronutrient Tracker — FastAPI application entry point.
"""

from fastapi import FastAPI

from .database import Base, engine
from .routers import auth

# Create all tables on startup (development convenience).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Calorie Tracker API",
    description="Track your calories and macronutrients",
    version="0.1.0",
)

# ── Routers ────────────────────────────────────────────────────
app.include_router(auth.router)


@app.get("/health", tags=["meta"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}
