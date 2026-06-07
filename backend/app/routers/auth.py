"""
Auth router — registration, login, and current-user retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import MacroTargets, Token, UserCreate, UserLogin, UserOut, UserUpdate
from ..services.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(tags=["auth"])


# ── Macro target calculation (Mifflin-St Jeor) ────────────────

_ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

_GOAL_ADJUSTMENTS = {
    "lose": -500,
    "maintain": 0,
    "gain": 300,
}


def _calculate_targets(user: User) -> dict:
    """
    Calculate personalised daily macro targets using Mifflin-St Jeor BMR.
    Returns a dict with calories, protein, carbs, fat, bmr, tdee, complete.
    """
    missing = not all([user.weight, user.height, user.age])
    if missing:
        return {
            "calories": 2000, "protein": 150, "carbs": 225, "fat": 67,
            "bmr": 0, "tdee": 0, "complete": False,
        }

    # BMR — Mifflin-St Jeor
    bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age
    if user.gender == "female":
        bmr -= 161
    else:
        bmr += 5  # male or unset

    # Total Daily Energy Expenditure
    multiplier = _ACTIVITY_MULTIPLIERS.get(user.activity_level or "sedentary", 1.4)
    tdee = bmr * multiplier

    # Calorie target adjusted for goal
    adjustment = _GOAL_ADJUSTMENTS.get(user.goal_type or "maintain", 0)
    target_calories = tdee + adjustment

    # Macro split
    # Protein: 2 g per kg of body weight
    # Fat:     25 % of target calories
    # Carbs:   everything that remains
    protein = user.weight * 2.0
    fat = (target_calories * 0.25) / 9
    carbs = (target_calories - protein * 4 - fat * 9) / 4

    return {
        "calories": round(target_calories),
        "protein":  round(protein),
        "carbs":    round(max(carbs, 50)),   # floor at 50 g
        "fat":      round(fat),
        "bmr":      round(bmr),
        "tdee":     round(tdee),
        "complete": True,
    }

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# ── Dependency: extract current user from JWT ──────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode the JWT, look up the user, and return the ORM object."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ── POST /register ─────────────────────────────────────────────

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account with a hashed password."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        weight=user_in.weight,
        height=user_in.height,
        age=user_in.age,
        activity_level=user_in.activity_level,
        goal_type=user_in.goal_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── POST /login ────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Validate credentials and return a JWT access token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# ── GET /me ────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user


# ── PUT /me ────────────────────────────────────────────────────

@router.put("/me", response_model=UserOut)
def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's body metrics and goals."""
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


# ── GET /me/targets ────────────────────────────────────────────

@router.get("/me/targets", response_model=MacroTargets)
def get_targets(current_user: User = Depends(get_current_user)):
    """
    Calculate and return the user's personalised daily macro targets
    based on their profile (weight, height, age, activity, goal).
    """
    return _calculate_targets(current_user)
