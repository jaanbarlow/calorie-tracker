# Calorie & Macronutrient Tracker

A full-stack calorie and macronutrient tracking app (FastAPI + PostgreSQL backend, React frontend).

## What this repo contains

- `backend/` – FastAPI app with authentication, food search, food logging, and daily summaries
- `frontend/` – Minimal React app (login/register, food search, dashboard)
- `docker-compose.yml` – Local development composition (Postgres, backend, frontend)

## Architecture

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Auth | JWT (python-jose) + passlib |
| Containers | Docker & Docker Compose |
| Frontend | React (Create React App) |

## Project Structure

```
calorie-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── models.py        # SQLAlchemy ORM models (includes FoodLog)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── database.py      # Database engine & session config
│   │   ├── routers/         # API route modules (auth.py, foods.py)
│   │   └── services/        # External API clients and services (food_api.py)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React app (login, register, search, dashboard)
├── docker-compose.yml
└── README.md
```

## Getting Started (development)

### Prerequisites

- Docker & Docker Compose

### Run locally

1. Copy or edit the `.env` file at the repo root and set `USDA_API_KEY` to your own key (recommended):

```bash
# Example (UNIX/macOS)
echo "USDA_API_KEY=your_real_key_here" >> .env
```

2. Build and start services:

```bash
docker compose up --build
```

Services:

- Backend: http://localhost:8000 (interactive docs: /docs)
- Frontend: http://localhost:3000

### Notes about the USDA API key

- The project includes a safe fallback `DEMO_KEY` for quick testing; this key is rate-limited. Put your own key in the `.env` file as `USDA_API_KEY` to avoid limits.
- `docker-compose.yml` forwards `USDA_API_KEY` into the backend container.

## API Endpoints (available now)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Create a new user account | No |
| POST | `/login` | Authenticate and receive JWT | No |
| GET | `/me` | Get current user profile | Yes |
| GET | `/foods/search?q=…` | Search USDA FoodData Central (returns calories/protein/carbs/fat per 100 g) | Yes |
| POST | `/foods/log` | Log a food entry (supply per-100g macros and `grams`; backend scales) | Yes |
| GET | `/foods/today` | Aggregated macros for today | Yes |
| GET | `/foods/logs` | Individual food logs for today | Yes |

## Security: keep secrets out of Git

The repo already ignores `.env` in `.gitignore`. Before committing, ensure you never add `.env` or other secret files to Git.

Recommended safe workflow (copyable commands):

```bash
# 1. Check current status
git status

# 2. Make sure .env is ignored and not staged. If it was staged accidentally, unstage and remove from index:
git restore --staged .env || true
git rm --cached .env || true

# 3. Review staged changes before committing
git add -A
git diff --staged --name-only

# 4. Commit with a clear message
git commit -m "feat: add food search and logging endpoints; frontend"

# 5. Push to remote
git push origin main
```

If you accidentally committed a secret (e.g., `.env`) to the remote, remove it from history promptly. A straightforward way to remove a file from the latest commit and rewrite history locally is:

```bash
# Remove file from all commits using git filter-repo (preferred) or BFG. Example using git filter-repo:
git filter-repo --path .env --invert-paths

# Force-push the cleaned history (communicate with your team first)
git push --force --all
```

If you can't use `git filter-repo`, use the BFG Repo-Cleaner or `git filter-branch` (older and slower). For sensitive leaks, also rotate the leaked secret (e.g. generate a new USDA key).

## What I changed recently (summary)

- Added `backend/app/services/food_api.py` — USDA client and nutrient extraction
- Added `backend/app/routers/foods.py` — endpoints for search, log, daily summary, and logs
- Added `FoodLog` model in `backend/app/models.py`
- Added Pydantic schemas in `backend/app/schemas.py`
- Registered foods router and enabled CORS in `backend/app/main.py`
- Added a minimal React frontend under `frontend/`
- Updated `docker-compose.yml` to pass `USDA_API_KEY` and add a frontend service

## Next steps (optional)

- Replace the demo USDA key with your own in `.env`
- Add server-side caching for USDA responses to reduce rate-limit issues
- Add deletion/edit endpoints for food logs and user-configurable daily targets

If you want, I can update `.env` with your real API key (not recommended to paste keys here). Instead, edit `.env` locally and rebuild the backend:

```bash
# Edit .env and set USDA_API_KEY; then rebuild backend
docker compose up --build backend
```

Questions or want me to add any of the optional improvements?
