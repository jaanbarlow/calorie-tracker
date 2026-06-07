"""
Agent router — conversational AI nutrition assistant endpoint.

POST /agent/chat
  Accepts the user's message and the prior conversation history,
  runs the LangChain tool-calling agent, and returns the AI response.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..routers.auth import get_current_user
from ..services.agent import run_agent

router = APIRouter(prefix="/agent", tags=["agent"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str   # "human" or "ai"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a message to the AI nutrition agent and receive a response.

    The client is responsible for maintaining conversation history and
    passing it back on each request. This keeps the backend stateless.
    """
    try:
        history = [{"role": m.role, "content": m.content} for m in body.history]
        response = run_agent(
            message=body.message,
            history=history,
            user=current_user,
            db=db,
        )
    except RuntimeError as exc:
        # OPENAI_API_KEY not configured
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Agent error: {exc}",
        )

    return {"response": response}
