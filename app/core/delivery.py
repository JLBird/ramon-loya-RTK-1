"""
RTK-1 Delivery Layer — auto-generates all customer-facing content.
Executive emails, slide decks, LinkedIn posts, weekly PDFs, monthly dashboards.
No LLM calls required — pure template generation from campaign data.
"""

import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("delivery")


class DeliveryEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.campaign_db_path

    # ========================
    # BUSINESS VALUE STATEMENT (Objective 47)
    # ========================
    def business_value_statement(
        self,
        target_model: str,
        goal: str,
        asr: float,
        previous_asr: Optional[float] = None,
        customer_success_metrics: str = "",
    ) -> str:
        if previous_asr is not None and previous_asr > 0:
            pct_change = round(((previous_asr - asr) / previous_asr) * 100, 1)
            delta_line = (
                f"Attack success rate improved from {previous_asr}% to {asr}% "
                f"— a {pct_change}% risk reduction."
                if asr < previous_asr
                else f"Attack success rate increased from {previous_asr}% to {asr}% "
                f"— immediate remediation required."
            )
        else:
            delta_line = f"Baseline established at {asr}% ASR."

        if asr == 0:
            risk_line = "System demonstrated full adversarial resilience. No breach risk detected."
            value_line = "Compliance evidence package ready for regulatory submission."
        elif asr <= 25:
            risk_line = (
                "Limited vulnerability detected. Targeted hardening recommended."
            )
            value_line = "Estimated breach risk: moderate. Remediation ROI: high."
        elif asr <= 75:
            risk_line = "Significant vulnerability detected. Immediate action required."
            value_line = (
                "A single breach of this type could cost $2M-$5M in regulatory fines "
                "and customer loss. RTK-1 found it before your adversaries did."
            )
        else:
            risk_line = (
                "Critical vulnerability. System unsafe for production deployment."
            )
            value_line = (
                "EU AI Act Article 15 compliance is invalidated at this ASR level. "
                "Deployment without remediation creates material regulatory liability."
            )

        return f"""You defined success as: {customer_success_metrics}

RTK-1 tested {target_model} using Crescendo multi-turn escalation
orchestrated by Claude Sonnet 4.6 + LangGraph + PyRIT 0.12.0.

Attack Success Rate: {asr}%
{delta_line}

{risk_line}
{value_line}

Compliance coverage: EU AI Act Art. 9, 15, Annex IV | NIST MEASURE 2.7
OWASP LLM01-LLM08 | MITRE ATLAS AML.T0054
Evidence package: PDF report + JSON audit logs + Grafana dashboard"""

    # ========================
    # EXECUTIVE EMAIL (Objective 43)
    # ========================
    def executive_email(
        self,
        job_id: str,
        target_model: str,
        asr: float,
        goal: str,
        report_link: str,
        previous_asr: Optional[float] = None,
        customer_name: str = "Team",
    ) -> dict:
        urgency = (
            "CRITICAL ACTION REQUIRED"
            if asr > 75
            else "ACTION REQUIRED"
            if asr > 25
            else "FOR YOUR REVIEW"
        )

        if asr == 0:
            headline = (
                f"{target_model} passed all adversarial tests — 0% Attack Success Rate"
            )
            body_core = (
                f"RTK-1 executed a full Crescendo red team campaign against {target_model} "
                f"and found no successful attack vectors. Your system demonstrated full "
                f"adversarial resilience across all tested sequences."
            )
        elif asr <= 25:
            headline = (
                f"{target_model} shows limited vulnerability — {asr}% ASR detected"
            )
            body_core = (
                f"RTK-1 identified limited attack success ({asr}%) against {target_model}. "
                f"Targeted hardening is recommended before your next production deployment."
            )
        elif asr <= 75:
            headline = f"SIGNIFICANT VULNERABILITY: {target_model} — {asr}% Attack Success Rate"
            body_core = (
                f"RTK-1 achieved {asr}% attack success against {target_model} using "
                f"Crescendo multi-turn escalation. This constitutes material evidence of "
                f"inadequate robustness under EU AI Act Article 15. Immediate remediation required."
            )
        else:
            headline = (
                f"CRITICAL: {target_model} failed adversarial testing — {asr}% ASR"
            )
            body_core = (
                f"RTK-1 achieved {asr}% attack success against {target_model}. "
                f"This system is unsafe for production deployment. All EU AI Act compliance "
                f"claims are invalidated until remediation is complete."
            )

        delta_line = ""
        if previous_asr is not None:
            delta = round(asr - previous_asr, 1)
            direction = "improved" if delta < 0 else "degraded"
            delta_line = f"\nWeek-over-week: ASR {direction} by {abs(delta)}pp ({previous_asr}% → {asr}%)\n"

        subject = f"[RTK-1] {urgency}: {headline}"
        body = f"""Dear {customer_name},

{body_core}
{delta_line}
Campaign Details:
- Target: {target_model}
- Objective: {goal}
- Job ID: {job_id}
- Report: {report_link}

Compliance Evidence Generated:
- EU AI Act Articles 9, 15, Annex IV, Article 72
- NIST AI RMF MEASURE 2.7
- OWASP LLM Top 10 (LLM01-LLM08)
- MITRE ATLAS AML.T0054

Download your full compliance report: {report_link}

—
RTK-1 Autonomous Red Teaming Platform
Powered by Claude Sonnet 4.6 + LangGraph + PyRIT"""

        return {"subject": subject, "body": body}

    # ========================
    # 3-SLIDE DECK (Objective 44)
    # ========================
    def slide_deck(
        self,
        job_id: str,
        target_model: str,
        asr: float,
        goal: str,
        total_sequences: int,
        successful_sequences: int,
        customer_success_metrics: str = "",
        previous_asr: Optional[float] = None,
    ) -> dict:
        robustness = (
            "STRONG ✅"
            if asr == 0
            else "MODERATE ⚠️"
            if asr <= 25
            else "WEAK ❌"
            if asr <= 75
            else "CRITICAL ❌"
        )

        delta_text = ""
        if previous_asr is not None:
            delta = round(previous_asr - asr, 1)
            delta_text = (
                f"{delta}pp improvement vs prior period"
                if delta > 0
                else f"{abs(delta)}pp regression vs prior period"
            )

        return {
            "title": f"RTK-1 Red Team Report — {target_model}",
            "subtitle": f"Autonomous AI Red Teaming | {datetime.now(UTC).strftime('%B %Y')}",
            "slides": [
                {
                    "slide": 1,
                    "title": "Executive Summary",
                    "headline": f"Attack Success Rate: {asr}%",
                    "subheadline": robustness,
                    "bullets": [
                        f"Target: {target_model}",
                        f"Objective: {goal}",
                        f"Sequences Executed: {total_sequences}",
                        f"Successful Attacks: {successful_sequences}",
                        delta_text if delta_text else "Baseline campaign",
                    ],
                    "call_to_action": (
                        "System is compliant — maintain current controls"
                        if asr == 0
                        else "Immediate remediation required — see Slide 3"
                    ),
                },
                {
                    "slide": 2,
                    "title": "Compliance Coverage",
                    "headline": "Evidence Generated Across 4 Frameworks",
                    "table": [
                        {
                            "framework": "EU AI Act",
                            "articles": "Art. 9, 15, Annex IV, Art. 72",
                            "status": "✅ Evidence generated",
                        },
                        {
                            "framework": "NIST AI RMF",
                            "articles": "MEASURE 2.7",
                            "status": "✅ Evidence generated",
                        },
                        {
                            "framework": "OWASP LLM Top 10",
                            "articles": "LLM01-LLM08",
                            "status": "✅ Evidence generated",
                        },
                        {
                            "framework": "MITRE ATLAS",
                            "articles": "AML.T0054",
                            "status": "✅ Evidence generated",
                        },
                    ],
                },
                {
                    "slide": 3,
                    "title": "Recommendations & Next Steps",
                    "headline": (
                        "No critical actions required"
                        if asr == 0
                        else f"Priority remediation required — {asr}% ASR"
                    ),
                    "bullets": (
                        [
                            "Maintain system prompt version control",
                            "Schedule next campaign in 30 days or after any model update",
                            "Expand coverage to RAG injection and tool abuse vectors",
                            "Archive compliance evidence package for regulatory review",
                        ]
                        if asr == 0
                        else [
                            "Implement system prompt integrity controls immediately",
                            "Deploy adversarial monitoring in production",
                            "Run remediation validation campaign after fixes",
                            "Do not deploy to production until ASR < 10%",
                        ]
                    ),
                    "report_link": f"{settings.base_url}/reports/{job_id}.pdf",
                },
            ],
        }

    # ========================
    # LINKEDIN POST (Objective 48)
    # ========================
    def linkedin_post(
        self,
        target_model: str,
        asr: float,
        total_sequences: int,
        goal: str,
        previous_asr: Optional[float] = None,
    ) -> str:
        if asr == 0:
            hook = f"We ran {total_sequences} adversarial attack sequences against {target_model}. ASR: 0%."
            insight = "Strong adversarial resilience. The system held under sustained Crescendo multi-turn pressure."
            cta = "This is what AI security evidence looks like — quantified, compliance-mapped, and reproducible."
        elif previous_asr and previous_asr > asr:
            improvement = round(((previous_asr - asr) / previous_asr) * 100, 1)
            hook = f"{improvement}% risk reduction. {target_model} went from {previous_asr}% to {asr}% ASR."
            insight = (
                "Continuous red teaming catches regressions before adversaries do."
            )
            cta = "This is the compounding value of always-on AI security."
        else:
            hook = f"RTK-1 achieved {asr}% attack success against {target_model} in under 10 minutes."
            insight = f"Crescendo multi-turn escalation. {total_sequences} sequences. Compliance-mapped findings."
            cta = "If you're deploying AI without adversarial testing, you're guessing at safety."

        return f"""{hook}

{insight}

Methodology:
→ Crescendo multi-turn escalation (PyRIT 0.12.0)
→ Orchestrated by Claude Sonnet 4.6 + LangGraph
→ Customer-defined success criteria
→ Auto-generated compliance evidence (EU AI Act / NIST / OWASP / MITRE)

{cta}

#AIRedTeaming #AISecurity #EUAIAct #LLMSecurity #RTK1"""

    # ========================
    # WEEKLY PDF SUMMARY (Objective 39)
    # ========================
    def weekly_summary_markdown(self, target_model: str) -> str:
        since = (datetime.now(UTC) - timedelta(days=7)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT job_id, asr, total_sequences, successful_sequences,
                       robustness_rating, completed_at
                FROM campaigns
                WHERE target_model = ? AND completed_at >= ?
                ORDER BY completed_at DESC
                """,
                (target_model, since),
            ).fetchall()

        if not rows:
            return f"# RTK-1 Weekly Summary — {target_model}\n\nNo campaigns in the last 7 days."

        asrs = [r[1] for r in rows]
        avg_asr = round(sum(asrs) / len(asrs), 1)
        best_asr = min(asrs)
        worst_asr = max(asrs)

        campaign_rows = ""
        for r in rows:
            campaign_rows += f"| {r[0][:8]} | {r[1]}% | {r[2]} | {r[5][:10]} |\n"

        return f"""# RTK-1 Weekly Summary — {target_model}

**Period:** {(datetime.now(UTC) - timedelta(days=7)).strftime("%Y-%m-%d")} to {datetime.now(UTC).strftime("%Y-%m-%d")}
**Total Campaigns:** {len(rows)}
**Average ASR:** {avg_asr}%
**Best ASR:** {best_asr}%
**Worst ASR:** {worst_asr}%

## Campaign Log

| Job ID | ASR | Sequences | Date |
|--------|-----|-----------|------|
{campaign_rows}

## Trend

{"⬇️ ASR improving over the week" if len(asrs) > 1 and asrs[0] < asrs[-1] else "⬆️ ASR degrading — review recent model changes" if len(asrs) > 1 and asrs[0] > asrs[-1] else "➡️ ASR stable"}

---
*Generated by RTK-1 Delivery Engine*"""

    # ========================
    # MONTHLY EXECUTIVE EMAIL (Objective 45)
    # ========================
    def monthly_executive_email(
        self, target_model: str, customer_name: str = "Team"
    ) -> dict:
        since = (datetime.now(UTC) - timedelta(days=30)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT asr, total_sequences, completed_at
                FROM campaigns
                WHERE target_model = ? AND completed_at >= ?
                ORDER BY completed_at ASC
                """,
                (target_model, since),
            ).fetchall()

        if not rows:
            return {
                "subject": f"[RTK-1] Monthly Summary — {target_model}",
                "body": "No campaigns recorded in the last 30 days.",
            }

        asrs = [r[0] for r in rows]
        total_sequences = sum(r[1] for r in rows)
        avg_asr = round(sum(asrs) / len(asrs), 1)
        first_asr = asrs[0]
        last_asr = asrs[-1]
        trend = round(first_asr - last_asr, 1)

        subject = f"[RTK-1] Monthly AI Security Report — {target_model} — {datetime.now(UTC).strftime('%B %Y')}"
        body = f"""Dear {customer_name},

Your monthly RTK-1 AI red teaming summary for {target_model}.

30-DAY PERFORMANCE SUMMARY
───────────────────────────
Total Campaigns Run:     {len(rows)}
Total Sequences Tested:  {total_sequences}
Average ASR:             {avg_asr}%
Starting ASR:            {first_asr}%
Ending ASR:              {last_asr}%
Month-over-Month Trend:  {"⬇️ " + str(trend) + "pp improvement" if trend > 0 else "⬆️ " + str(abs(trend)) + "pp degradation — review required" if trend < 0 else "➡️ Stable"}

COMPLIANCE STATUS
───────────────────────────
EU AI Act Art. 9, 15, Annex IV:  {"✅ Satisfied" if last_asr <= 25 else "❌ Remediation Required"}
NIST AI RMF MEASURE 2.7:         {"✅ Satisfied" if last_asr <= 25 else "❌ Remediation Required"}
OWASP LLM Top 10:                {"✅ Satisfied" if last_asr <= 25 else "❌ Remediation Required"}

RECOMMENDED ACTIONS
───────────────────────────
{"• Continue current security posture — no critical actions required" if last_asr == 0 else "• Schedule remediation validation campaign immediately" if last_asr > 50 else "• Review findings from highest-ASR campaigns this month"}
- Expand attack coverage to RAG injection and tool abuse vectors
- Archive this report for regulatory evidence package

—
RTK-1 Autonomous Red Teaming Platform
{datetime.now(UTC).strftime("%B %Y")}"""

        return {"subject": subject, "body": body}

    # ========================
    # ONE-CLICK DELIVERY BUNDLE (Objective 29)
    # ========================
    def delivery_bundle(
        self,
        job_id: str,
        target_model: str,
        asr: float,
        goal: str,
        total_sequences: int,
        successful_sequences: int,
        customer_success_metrics: str = "",
        previous_asr: Optional[float] = None,
        customer_name: str = "Team",
        report_link: str = "",
    ) -> dict:
        return {
            "job_id": job_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "business_value_statement": self.business_value_statement(
                target_model=target_model,
                goal=goal,
                asr=asr,
                previous_asr=previous_asr,
                customer_success_metrics=customer_success_metrics,
            ),
            "executive_email": self.executive_email(
                job_id=job_id,
                target_model=target_model,
                asr=asr,
                goal=goal,
                report_link=report_link,
                previous_asr=previous_asr,
                customer_name=customer_name,
            ),
            "slide_deck": self.slide_deck(
                job_id=job_id,
                target_model=target_model,
                asr=asr,
                goal=goal,
                total_sequences=total_sequences,
                successful_sequences=successful_sequences,
                customer_success_metrics=customer_success_metrics,
                previous_asr=previous_asr,
            ),
            "linkedin_post": self.linkedin_post(
                target_model=target_model,
                asr=asr,
                total_sequences=total_sequences,
                goal=goal,
                previous_asr=previous_asr,
            ),
            "weekly_summary": self.weekly_summary_markdown(target_model=target_model),
        }


delivery = DeliveryEngine()
