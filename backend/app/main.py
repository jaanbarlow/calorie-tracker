"""
Calorie & Macronutrient Tracker — FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, foods

# Create all tables on startup (development convenience).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Calorie Tracker API",
    description="Track your calories and macronutrients",
    version="0.1.0",
)

# ── CORS (allow the React dev server) ─────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(foods.router)


@app.get("/health", tags=["meta"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}
