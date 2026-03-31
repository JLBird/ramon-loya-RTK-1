import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.orchestrator.claude_orchestrator import compiled_graph

router = APIRouter(tags=["redteam"])


class RedTeamRequest(BaseModel):
    target_model: str
    goal: str
    attack_type: Literal["single-turn", "crescendo", "tap", "agent-tool-calling"] = (
        "crescendo"
    )


@router.post("/redteam/crescendo")
async def run_crescendo(req: RedTeamRequest):
    """Multi-turn gradual escalation attack (Claude decides the chain)."""
    if not settings.anthropic_api_key or not settings.anthropic_api_key.startswith(
        "sk-ant-"
    ):
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    initial_state = {
        "target_model": req.target_model,
        "goal": req.goal,
        "attack_type": req.attack_type,
    }

    try:
        # Fixed thread_id for LangGraph checkpoint (MemorySaver)
        config = {"configurable": {"thread_id": f"job-{str(uuid.uuid4())}"}}
        result = await compiled_graph.ainvoke(initial_state, config=config)

        return {
            "job_id": config["configurable"]["thread_id"],
            "status": "completed",
            "attack_type": req.attack_type,
            "results": result.get("results", []),
            "reflection": result.get("reflection"),
            "attack_plan": result.get("attack_plan"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redteam/tap")
async def run_tap(req: RedTeamRequest):
    """Tree-of-Attacks placeholder."""
    return {"message": "TAP endpoint coming soon"}
