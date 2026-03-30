from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from app.orchestrator.claude_orchestrator import compiled_graph  # We'll create this next
from app.core.config import settings

router = APIRouter(tags=["redteam"])

class RedTeamRequest(BaseModel):
    target_model: str                          # e.g. "ollama:llama3.2" or "openai:gpt-4o"
    goal: str                                  # e.g. "Test for prompt injection on RAG chatbot"
    attack_type: Literal["single-turn", "crescendo", "tap", "agent-tool-calling"] = "crescendo"

@router.post("/redteam/crescendo")
async def run_crescendo(req: RedTeamRequest):
    """Multi-turn gradual escalation attack (Claude decides the chain)."""
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
    
    initial_state = {"target_model": req.target_model, "goal": req.goal}
    try:
        result = await compiled_graph.ainvoke(initial_state)
        return {
            "job_id": f"job-{hash(str(result))}",
            "status": "completed",
            "attack_type": "crescendo",
            "results": result.get("results", []),
            "reflection": result.get("reflection")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Placeholder for other endpoints (we'll expand these next)
@router.post("/redteam/tap")
async def run_tap(req: RedTeamRequest):
    """Tree-of-Attacks with pruning (Claude builds & prunes the tree)."""
    return {"message": "TAP endpoint coming in next step (Claude orchestrator ready)"}