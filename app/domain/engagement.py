"""
RTK-1 Engagement Configuration — structured customer intake.
Replaces free-text success metrics with a typed, validated model.
Every downstream component derives its configuration from this.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.models import AttackTool, AttackVector


class RiskTier(str, Enum):
    """EU AI Act risk classification."""

    UNACCEPTABLE = "unacceptable"  # Banned
    HIGH = "high"  # Full compliance required
    LIMITED = "limited"  # Transparency obligations
    MINIMAL = "minimal"  # No specific obligations


class ComplianceTarget(str, Enum):
    EU_AI_ACT = "eu_ai_act"
    NIST_AI_RMF = "nist_ai_rmf"
    OWASP_LLM = "owasp_llm"
    MITRE_ATLAS = "mitre_atlas"
    SOC2 = "soc2"
    ISO_27001 = "iso_27001"


class SuccessCriteria(BaseModel):
    """
    What the customer says success looks like.
    This drives the scorer, the report framing, and the compliance mapping.
    """

    primary_goal: str = Field(
        description="The single most important outcome this engagement must demonstrate"
    )
    acceptable_asr_threshold: float = Field(
        default=10.0,
        ge=0.0,
        le=100.0,
        description="Max acceptable ASR % — above this is a compliance failure",
    )
    must_prove_resilience_to: List[str] = Field(
        default_factory=list,
        description="Specific attack classes customer needs proof against",
    )
    thirty_day_outcomes: List[str] = Field(
        default_factory=list,
        description="What customer expects to be able to do 30 days after engagement",
    )


class EngagementConfig(BaseModel):
    """
    Complete customer engagement specification.
    Single source of truth for a campaign — created at intake,
    drives everything downstream including scorer, report, and alerts.
    """

    engagement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Customer context
    customer_name: str = "Internal"
    customer_industry: Optional[str] = None
    contact_email: Optional[str] = None

    # Target system
    target_model: str
    target_description: Optional[str] = None
    target_environment: str = "staging"  # staging, production, shadow

    # Attack configuration
    attack_vectors: List[AttackVector] = Field(
        default_factory=lambda: [AttackVector.CRESCENDO]
    )
    preferred_tool: AttackTool = AttackTool.PYRIT
    num_sequences: int = Field(default=3, ge=1, le=50)
    turns_per_sequence: int = Field(default=8, ge=1, le=20)

    # Risk and compliance
    risk_tier: RiskTier = RiskTier.HIGH
    compliance_targets: List[ComplianceTarget] = Field(
        default_factory=lambda: [
            ComplianceTarget.EU_AI_ACT,
            ComplianceTarget.NIST_AI_RMF,
            ComplianceTarget.OWASP_LLM,
            ComplianceTarget.MITRE_ATLAS,
        ]
    )

    # Success definition
    success_criteria: SuccessCriteria

    # Delivery preferences
    generate_pdf: bool = True
    send_slack_alert: bool = True
    post_to_pr: bool = False
    webhook_url: Optional[str] = None

    @property
    def customer_success_metrics_summary(self) -> str:
        """Formatted summary for report headers and scorer generation."""
        lines = [f"Primary Goal: {self.success_criteria.primary_goal}"]
        if self.success_criteria.must_prove_resilience_to:
            lines.append(
                f"Must prove resilience to: {', '.join(self.success_criteria.must_prove_resilience_to)}"
            )
        if self.success_criteria.thirty_day_outcomes:
            lines.append("30-day outcomes:")
            for outcome in self.success_criteria.thirty_day_outcomes:
                lines.append(f"  - {outcome}")
        return "\n".join(lines)

    @property
    def compliance_frameworks_list(self) -> List[str]:
        """Human-readable compliance framework names."""
        mapping = {
            ComplianceTarget.EU_AI_ACT: "EU AI Act (Articles 9, 15, Annex IV)",
            ComplianceTarget.NIST_AI_RMF: "NIST AI RMF 1.0 — MEASURE 2.7",
            ComplianceTarget.OWASP_LLM: "OWASP LLM Top 10 — LLM01",
            ComplianceTarget.MITRE_ATLAS: "MITRE ATLAS — AML.T0054",
            ComplianceTarget.SOC2: "SOC 2 Type II",
            ComplianceTarget.ISO_27001: "ISO 27001",
        }
        return [mapping[t] for t in self.compliance_targets]
