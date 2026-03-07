# Calorie & Macronutrient Tracker

A full-stack app for tracking calories and macronutrients, built with a FastAPI + PostgreSQL backend and a React frontend.

## Overview

This project lets users:

- Register and log in with JWT authentication
- Search foods from USDA FoodData Central
- Log food entries in grams
- View daily macro totals (calories, protein, carbs, fat)
- View today’s individual food logs

## Architecture

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Auth | JWT (`python-jose`) + `passlib` |
| Containers | Docker & Docker Compose |
| Frontend | React (Create React App) |

## Project Structure

```text
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
├── frontend/                # React app (login, register, search, dashboard)
├── docker-compose.yml
└── README.md
```

## Boot Up

### Run with Docker

From the project root:

```bash
docker compose up --build
```

Then open:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

To stop:

```bash
docker compose down
```
