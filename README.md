# Calorie & Macronutrient Tracker

A full-stack calorie and macronutrient tracking application.

## Architecture

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Auth | JWT (python-jose) + passlib |
| Containers | Docker & Docker Compose |
| Frontend | TBD (future phase) |

## Project Structure

```
calorie-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── database.py      # Database engine & session config
│   │   ├── routers/         # API route modules
│   │   │   └── auth.py      # /register, /login, /me
│   │   └── services/        # Business logic
│   │       └── auth.py      # Password hashing, JWT creation/verification
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Future phase
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Docker & Docker Compose

### Run

```bash
docker compose up --build
```

The API will be available at **http://localhost:8000**.

Interactive docs: **http://localhost:8000/docs**

### API Endpoints (Phase 2)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Create a new user account | No |
| POST | `/login` | Authenticate and receive JWT | No |
| GET | `/me` | Get current user profile | Yes |

### Environment Variables

Configured in `docker-compose.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@postgres:5432/calorietracker` |
| `SECRET_KEY` | JWT signing secret | `super-secret-change-me-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL | `60` |
