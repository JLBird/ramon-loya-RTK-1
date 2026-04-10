"""
RTK-1 Domain Models — stable regardless of underlying provider changes.
All orchestration layer nodes see only these models, never raw dicts or provider objects.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AttackOutcome(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    UNDETERMINED = "undetermined"
    ERROR = "error"


class AttackVector(str, Enum):
    CRESCENDO = "crescendo"
    SINGLE_TURN = "single-turn"
    TAP = "tap"
    AGENT_TOOL_CALLING = "agent-tool-calling"


class AttackTool(str, Enum):
    PYRIT = "pyrit"
    GARAK = "garak"
    PROMPTFOO = "promptfoo"
    CREWAI = "crewai"
    DEEPTEAM = "deepteam"
    MOCK = "mock"
    RAG_INJECTION = "rag_injection"
    TOOL_ABUSE = "tool_abuse"


class AttackResult(BaseModel):
    """
    Single attack sequence result — stable domain model.
    Never expose raw PyRIT/Garak/promptfoo objects above this layer.
    """

    sequence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step: int
    turn_number: int = 0
    escalation_depth: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tool_used: AttackTool = AttackTool.PYRIT
    vector: AttackVector = AttackVector.CRESCENDO
    objective: str
    prompt: str
    response: str
    outcome: AttackOutcome = AttackOutcome.UNDETERMINED
    success: bool = False
    description: str
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class ScorerConfig(BaseModel):
    """Customer-defined scorer configuration — derived from success metrics."""

    true_description: str
    false_description: str
    objective_summary: str


class CampaignConfig(BaseModel):
    """
    Full campaign configuration — created at intake, drives everything downstream.
    This is the single source of truth for what the customer wants.
    """

    campaign_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_model: str
    goal: str
    vector: AttackVector = AttackVector.CRESCENDO
    tool: AttackTool = AttackTool.PYRIT
    customer_success_metrics: str
    scorer_config: Optional[ScorerConfig] = None
    num_sequences: int = 3
    turns_per_sequence: int = 8
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OrchestratorResult(BaseModel):
    """
    Final output of a completed campaign — returned by the facade.
    Clean, stable, no provider leakage.
    """

    campaign_id: str
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "completed"
    vector: AttackVector
    tool_used: AttackTool
    target_model: str
    goal: str
    customer_success_metrics: str
    total_sequences: int
    successful_sequences: int
    asr: float
    results: List[AttackResult] = Field(default_factory=list)
    final_report_markdown: Optional[str] = None
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def failed_sequences(self) -> int:
        return self.total_sequences - self.successful_sequences
