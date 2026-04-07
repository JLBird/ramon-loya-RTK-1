from datetime import UTC, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.domain.models import AttackResult

AttackType = Literal["single-turn", "crescendo", "tap", "agent-tool-calling"]

CampaignStatus = Literal[
    "completed",
    "pre_execution_baseline",
    "running",
    "failed",
    "awaiting_human_approval",
]


class RedTeamRequest(BaseModel):
    target_model: str
    goal: str
    attack_type: AttackType = "crescendo"
    customer_success_metrics: str = "Not specified in this run"


class SupervisorDecision(BaseModel):
    next_action: Literal[
        "run_attack", "generate_report", "human_approval", "end_campaign"
    ]
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_tool: Optional[Literal["pyrit", "garak"]] = None


class CampaignResult(BaseModel):
    """Legacy schema — orchestrator now uses domain.models.AttackResult internally."""

    step: int
    turn_number: int = 0
    escalation_depth: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    description: str
    prompt: str
    response: str
    success: bool


class RedTeamResponse(BaseModel):
    job_id: str
    status: CampaignStatus
    attack_type: AttackType
    total_sequences: int
    sequences_run: int = 0
    asr: float = Field(ge=0.0, le=100.0)
    results: Optional[List[AttackResult]] = None
    final_report_markdown: str
    report_link: Optional[str] = None
    grafana_link: Optional[str] = None
    customer_success_mapped: bool = False

    @model_validator(mode="after")
    def compute_customer_success_mapped(self):
        if self.final_report_markdown:
            self.customer_success_mapped = (
                "success metrics" in self.final_report_markdown.lower()
                or "customer-defined" in self.final_report_markdown.lower()
            )
        return self
