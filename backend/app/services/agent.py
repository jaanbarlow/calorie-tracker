"""
AI Nutrition Agent — LangChain tool-calling agent powered by GPT-4o-mini.

The agent is built fresh per request so that every tool closure is bound
to the correct authenticated user and their active DB session.

Tools available to the agent:
  • get_daily_summary   — today's macro totals from the DB
  • get_food_history    — per-day macro totals for the last N days
  • search_food         — USDA FoodData Central search
  • log_food            — write a FoodLog row for the current user
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from sqlalchemy import cast, Date, func
from sqlalchemy.orm import Session

from ..models import FoodLog, User
from ..services.food_api import search_foods as usda_search


# ── LLM ───────────────────────────────────────────────────────────────────────

def _get_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set. "
            "Add it to your .env file or docker-compose.yml."
        )
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)


# ── System prompt ─────────────────────────────────────────────────────────────

def _build_system_prompt(user: User) -> str:
    profile_lines: list[str] = []
    if user.weight:
        profile_lines.append(f"- Weight: {user.weight} kg")
    if user.height:
        profile_lines.append(f"- Height: {user.height} cm")
    if user.age:
        profile_lines.append(f"- Age: {user.age}")
    if user.activity_level:
        profile_lines.append(f"- Activity level: {user.activity_level}")
    if user.goal_type:
        profile_lines.append(f"- Goal: {user.goal_type}")

    profile_section = (
        "\n".join(profile_lines)
        if profile_lines
        else "No profile data provided yet."
    )

    return f"""You are a knowledgeable and friendly AI nutrition coach assistant.
You help the user track their food intake, understand their macronutrient balance,
and make progress toward their health goals.

User profile:
{profile_section}

Today's date: {date.today().isoformat()}

Guidelines:
- Always use your tools to fetch real data before making claims about what the
  user has eaten or their current macro totals.
- When the user asks to log food, first search for it with search_food to get
  accurate nutritional values, then call log_food with the best match.
- Be concise but warm. Use numbers from the tools, not guesses.
- If the user has no profile data, gently encourage them to fill it in so you
  can give personalised calorie and macro recommendations.
- When analysing trends, use get_food_history to look at multiple days.
"""


# ── Tool factory ──────────────────────────────────────────────────────────────

def _make_tools(user: User, db: Session) -> list:
    """Return a fresh list of tools bound to *user* and *db*."""

    # ── Tool 1: daily summary ──────────────────────────────────────────────────
    @tool
    def get_daily_summary() -> dict[str, Any]:
        """
        Return the total calories, protein, carbs, and fat the user has
        logged TODAY.  Call this whenever the user asks how much they have
        eaten or whether they are hitting a macro goal.
        """
        today = date.today()
        row = (
            db.query(
                func.coalesce(func.sum(FoodLog.calories), 0),
                func.coalesce(func.sum(FoodLog.protein), 0),
                func.coalesce(func.sum(FoodLog.carbs), 0),
                func.coalesce(func.sum(FoodLog.fat), 0),
            )
            .filter(
                FoodLog.user_id == user.id,
                cast(FoodLog.created_at, Date) == today,
            )
            .first()
        )
        return {
            "date": today.isoformat(),
            "calories": round(float(row[0]), 1),
            "protein_g": round(float(row[1]), 1),
            "carbs_g": round(float(row[2]), 1),
            "fat_g": round(float(row[3]), 1),
        }

    # ── Tool 2: food history ───────────────────────────────────────────────────
    @tool
    def get_food_history(days: int = 7) -> list[dict[str, Any]]:
        """
        Return per-day macro totals for the last *days* days (default 7).
        Use this to analyse trends, spot patterns, or answer questions like
        'how has my protein intake been this week?'

        Args:
            days: How many past days to include (1–30).
        """
        days = max(1, min(days, 30))
        start = date.today() - timedelta(days=days - 1)

        rows = (
            db.query(
                cast(FoodLog.created_at, Date).label("day"),
                func.coalesce(func.sum(FoodLog.calories), 0).label("calories"),
                func.coalesce(func.sum(FoodLog.protein), 0).label("protein"),
                func.coalesce(func.sum(FoodLog.carbs), 0).label("carbs"),
                func.coalesce(func.sum(FoodLog.fat), 0).label("fat"),
            )
            .filter(
                FoodLog.user_id == user.id,
                cast(FoodLog.created_at, Date) >= start,
            )
            .group_by(cast(FoodLog.created_at, Date))
            .order_by(cast(FoodLog.created_at, Date))
            .all()
        )

        return [
            {
                "date": str(r.day),
                "calories": round(float(r.calories), 1),
                "protein_g": round(float(r.protein), 1),
                "carbs_g": round(float(r.carbs), 1),
                "fat_g": round(float(r.fat), 1),
            }
            for r in rows
        ]

    # ── Tool 3: search food ────────────────────────────────────────────────────
    @tool
    def search_food(query: str) -> list[dict[str, Any]]:
        """
        Search the USDA FoodData Central database for foods matching *query*.
        Returns up to 5 results, each with fdc_id, name, calories, protein,
        carbs, and fat — all per 100 g.

        Always call this BEFORE log_food so you have accurate nutritional data.

        Args:
            query: The food name to search for (e.g. 'chicken breast', 'banana').
        """
        results = usda_search(query, max_results=5)
        return results

    # ── Tool 4: log food ───────────────────────────────────────────────────────
    @tool
    def log_food(
        food_name: str,
        grams: float,
        calories_per_100g: float,
        protein_per_100g: float,
        carbs_per_100g: float,
        fat_per_100g: float,
    ) -> str:
        """
        Log a food entry for the user. Macro values must be PER 100 G —
        the backend scales them by grams/100 automatically.

        Always call search_food first to get accurate nutritional values,
        then pass the best-matching food's data here.

        Args:
            food_name:          Human-readable name of the food.
            grams:              How many grams the user consumed.
            calories_per_100g:  Calories per 100 g.
            protein_per_100g:   Protein grams per 100 g.
            carbs_per_100g:     Carbohydrate grams per 100 g.
            fat_per_100g:       Fat grams per 100 g.
        """
        scale = grams / 100.0
        entry = FoodLog(
            user_id=user.id,
            food_name=food_name,
            grams=round(grams, 2),
            calories=round(calories_per_100g * scale, 2),
            protein=round(protein_per_100g * scale, 2),
            carbs=round(carbs_per_100g * scale, 2),
            fat=round(fat_per_100g * scale, 2),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return (
            f"Logged {grams}g of {food_name}: "
            f"{entry.calories} kcal, {entry.protein}g protein, "
            f"{entry.carbs}g carbs, {entry.fat}g fat."
        )

    return [get_daily_summary, get_food_history, search_food, log_food]


# ── Public API ────────────────────────────────────────────────────────────────

def run_agent(
    message: str,
    history: list[dict[str, str]],
    user: User,
    db: Session,
) -> str:
    """
    Run the nutrition agent for one turn.

    Args:
        message:  The user's latest message.
        history:  Previous turns as a list of {"role": "human"|"ai",
                  "content": "..."} dicts.
        user:     Authenticated SQLAlchemy User object.
        db:       Active SQLAlchemy session.

    Returns:
        The agent's text response.
    """
    llm = _get_llm()
    tools = _make_tools(user, db)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _build_system_prompt(user)),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    # Convert history dicts → LangChain message objects
    lc_history = []
    for msg in history:
        if msg["role"] == "human":
            lc_history.append(HumanMessage(content=msg["content"]))
        else:
            lc_history.append(AIMessage(content=msg["content"]))

    result = executor.invoke(
        {"input": message, "chat_history": lc_history}
    )
    return result["output"]
