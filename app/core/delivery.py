"""
RTK-1 Delivery Layer — auto-generates all client-facing content.
PDF reports, executive emails, slide decks, LinkedIn posts,
business value statements, weekly/monthly summaries.
All generated from campaign data — no manual work required.
"""

from datetime import UTC, datetime
from typing import Optional

from app.core.history import history
from app.core.logging import get_logger

logger = get_logger("delivery")


class DeliveryManager:
    """
    Generates all client-facing deliverables from campaign data.
    One-click delivery bundle: PDF + email + deck + dashboard link.
    """

    # ========================
    # BUSINESS VALUE STATEMENT (Objective 47)
    # ========================
    def generate_business_value_statement(
        self,
        target_model: str,
        goal: str,
        asr: float,
        total_sequences: int,
        customer_success_metrics: str,
        job_id: str,
    ) -> str:
        """
        Generates the core business value statement.
        Powers all other deliverables.
        """
        delta = history.get_asr_delta(target_model=target_model)
        prev_asr = delta.get("previous_asr", asr)
        pct_change = delta.get("pct_change", 0.0)
        framing = delta.get("framing", f"Current ASR: {asr}%")

        if asr == 0.0:
            risk_level = "minimal"
            verdict = (
                "Your system demonstrated full resilience to all tested attack vectors."
            )
            financial = "Zero exploitable vulnerabilities detected — compliance claims are fully substantiated."
        elif asr <= 25.0:
            risk_level = "low"
            verdict = "Your system showed strong but imperfect defenses. Targeted hardening recommended."
            financial = f"At {asr}% ASR, limited exposure exists. Estimated risk: low-moderate regulatory exposure."
        elif asr <= 75.0:
            risk_level = "elevated"
            verdict = "Your system has meaningful vulnerabilities requiring immediate remediation."
            financial = f"At {asr}% ASR, a single breach could cost $1M-$5M in regulatory fines and customer loss."
        else:
            risk_level = "critical"
            verdict = "Your system is highly vulnerable. Deployment is not recommended without remediation."
            financial = f"At {asr}% ASR, estimated breach exposure exceeds $5M. Immediate action required."

        improvement = ""
        if pct_change > 0 and prev_asr > asr:
            improvement = (
                f"\n\nWeek-over-week improvement: ASR dropped from {prev_asr:.1f}% "
                f"to {asr:.1f}% — risk reduced {pct_change:.0f}%. "
                f"Our red teaming saved an estimated "
                f"${(prev_asr - asr) * 100000:.0f} in risk exposure this week."
            )

        return f"""You defined success as: {customer_success_metrics}

RTK-1 tested {total_sequences} attack sequences against {target_model} using \
Claude Sonnet 4.6 orchestration + LangGraph stateful checkpoints + FastAPI \
production backend.

Result: Attack Success Rate = {asr}% ({risk_level} risk)
{verdict}
{financial}{improvement}

Evidence: PDF report + JSON audit logs + Grafana dashboard
Report ID: RTK1-{job_id[:8].upper()}
Compliance: EU AI Act Articles 9, 15, Annex IV | NIST MEASURE 2.7 | OWASP LLM01-LLM08"""

    # ========================
    # EXECUTIVE EMAIL (Objective 43)
    # ========================
    def generate_executive_email(
        self,
        target_model: str,
        goal: str,
        asr: float,
        total_sequences: int,
        customer_success_metrics: str,
        job_id: str,
        recipient_name: str = "Team",
        report_link: Optional[str] = None,
        grafana_link: Optional[str] = None,
    ) -> dict:
        """Generates executive email ready to send."""
        bvs = self.generate_business_value_statement(
            target_model, goal, asr, total_sequences, customer_success_metrics, job_id
        )

        if asr == 0.0:
            subject = f"✅ AI Red Team Results: {target_model} PASSED — ASR 0%"
            urgency = "Good news"
        elif asr <= 25.0:
            subject = (
                f"⚠️ AI Red Team Results: {target_model} — {asr}% ASR, Minor Issues"
            )
            urgency = "Action recommended"
        else:
            subject = f"🚨 URGENT: AI Red Team Results — {target_model} at {asr}% ASR"
            urgency = "Immediate action required"

        report_section = ""
        if report_link:
            report_section = f"\nFull Report: {report_link}"
        if grafana_link:
            report_section += f"\nLive Dashboard: {grafana_link}"

        body = f"""Hi {recipient_name},

{urgency} — here are the results from our latest AI red teaming campaign.

{bvs}
{report_section}

Next steps are outlined in the attached PDF report. Please review Priority 1 \
mitigations before the next deployment.

Best regards,
RTK-1 AI Red Team
Campaign ID: RTK1-{job_id[:8].upper()}
Generated: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")}"""

        return {
            "subject": subject,
            "body": body,
            "job_id": job_id,
            "asr": asr,
        }

    # ========================
    # 3-SLIDE DECK (Objective 44)
    # ========================
    def generate_slide_deck_content(
        self,
        target_model: str,
        goal: str,
        asr: float,
        total_sequences: int,
        customer_success_metrics: str,
        job_id: str,
        report_link: Optional[str] = None,
        grafana_link: Optional[str] = None,
    ) -> dict:
        """
        Generates 3-slide deck content.
        Slide 1: Executive summary + key number
        Slide 2: Findings + compliance status
        Slide 3: Next steps + business value
        """
        delta = history.get_asr_delta(target_model=target_model)
        framing = delta.get("framing", f"ASR: {asr}%")
        business_value = delta.get("business_value", "")

        if asr == 0.0:
            verdict_color = "GREEN"
            verdict_text = "PASSED — Full Resilience Demonstrated"
        elif asr <= 25.0:
            verdict_color = "YELLOW"
            verdict_text = "MODERATE RISK — Targeted Hardening Required"
        else:
            verdict_color = "RED"
            verdict_text = "HIGH RISK — Immediate Remediation Required"

        return {
            "deck_title": f"AI Red Team Report — {target_model}",
            "generated_at": datetime.now(UTC).strftime("%Y-%m-%d"),
            "slides": [
                {
                    "number": 1,
                    "title": "Executive Summary",
                    "headline": f"Attack Success Rate: {asr}%",
                    "verdict": verdict_text,
                    "verdict_color": verdict_color,
                    "bullets": [
                        f"Target: {target_model}",
                        f"Objective: {goal}",
                        f"Sequences tested: {total_sequences}",
                        "Methodology: Crescendo Multi-Turn Escalation (PyRIT 0.12.0)",
                        "Orchestration: Claude Sonnet 4.6 + LangGraph",
                    ],
                    "key_number": f"{asr}%",
                    "key_label": "Attack Success Rate",
                },
                {
                    "number": 2,
                    "title": "Findings & Compliance",
                    "headline": framing,
                    "bullets": [
                        f"EU AI Act Articles 9, 15, Annex IV: {'✅ Satisfied' if asr == 0 else '❌ Remediation Required'}",
                        f"NIST AI RMF MEASURE 2.7: {'✅ Satisfied' if asr == 0 else '❌ Remediation Required'}",
                        f"OWASP LLM01 Prompt Injection: {'✅ Defended' if asr == 0 else f'❌ {asr}% bypass rate'}",
                        f"MITRE ATLAS AML.T0054: {'✅ Mitigated' if asr == 0 else '❌ Exploitable'}",
                        business_value,
                    ],
                    "report_link": report_link or "",
                    "grafana_link": grafana_link or "",
                },
                {
                    "number": 3,
                    "title": "Next Steps & Business Value",
                    "headline": "Actionable Mitigations + Proof of Safety",
                    "bullets": [
                        "0-30 Days: Archive report, brief legal/compliance/product leadership",
                        "0-30 Days: Implement Priority 1 system prompt integrity controls"
                        if asr > 0
                        else "0-30 Days: Confirm version control procedures",
                        "30-90 Days: Integrate test cases into CI/CD pipeline as regression gates",
                        "30-90 Days: Establish production monitoring baselines",
                        "90+ Days: Commission expanded campaign (RAG injection, data extraction)",
                    ],
                    "value_statement": (
                        f"A single breach could cost $5M+ in fines and customer loss. "
                        f"This engagement {'reduced that risk to near zero' if asr == 0 else f'identified {asr}% exposure — remediation is your next investment'}."
                    ),
                },
            ],
        }

    # ========================
    # WEEKLY PDF REPORT (Objective 39)
    # ========================
    def generate_weekly_summary_markdown(
        self,
        target_model: str,
        days: int = 7,
    ) -> str:
        """Generates weekly summary markdown for PDF rendering."""
        trend = history.get_asr_trend(target_model=target_model, days=days)
        delta = history.get_asr_delta(target_model=target_model)
        latest = history.get_latest_campaign(target_model=target_model)

        generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        week_start = datetime.now(UTC).strftime("%Y-%m-%d")

        if not trend:
            return f"""# RTK-1 Weekly Red Team Summary
**Week of:** {week_start}
**Target:** {target_model}
**Generated:** {generated_at}

No campaigns executed this week. Schedule a campaign to generate data.
"""

        current_asr = delta.get("current_asr", 0.0)
        framing = delta.get("framing", "No prior week data")
        business_value = delta.get("business_value", "")
        campaigns_this_week = delta.get("this_week_campaigns", len(trend))

        trend_rows = ""
        for entry in trend:
            trend_rows += (
                f"| {entry['completed_at'][:10]} "
                f"| {entry['asr']}% "
                f"| {entry['robustness_rating']} "
                f"| `{entry.get('git_commit', 'unknown')}` |\n"
            )

        return f"""# RTK-1 Weekly Red Team Summary

**Week of:** {week_start}
**Target Model:** `{target_model}`
**Generated:** {generated_at}
**Classification:** Confidential — Internal Use Only

---

## Week at a Glance

| Metric | Value |
|--------|-------|
| Campaigns This Week | {campaigns_this_week} |
| Current ASR | {current_asr}% |
| Week-over-Week | {framing} |

{business_value}

---

## Campaign History (Last {days} Days)

| Date | ASR | Rating | Git Commit |
|------|-----|--------|------------|
{trend_rows}

---

## Trending

{framing}

{business_value}

---

*Generated by RTK-1 Weekly Reporter*
*Always-on AI red teaming — protecting production 24/7*
"""

    # ========================
    # MONTHLY EXECUTIVE DASHBOARD EMAIL (Objective 45)
    # ========================
    def generate_monthly_executive_email(
        self,
        target_model: str,
    ) -> dict:
        """Generates monthly executive dashboard email."""
        trend_30 = history.get_asr_trend(target_model=target_model, days=30)
        delta = history.get_asr_delta(target_model=target_model)
        latest = history.get_latest_campaign(target_model=target_model)

        month = datetime.now(UTC).strftime("%B %Y")
        current_asr = delta.get("current_asr", 0.0)
        pct_change = delta.get("pct_change", 0.0)
        campaigns = len(trend_30)
        framing = delta.get("framing", "Baseline established")
        business_value = delta.get("business_value", "")

        improvement_line = ""
        if pct_change > 0 and delta.get("delta", 0) < 0:
            improvement_line = (
                f"This month we reduced attack success rate by {pct_change:.0f}%, "
                f"demonstrating measurable improvement in AI system robustness."
            )
        elif delta.get("delta", 0) > 0:
            improvement_line = (
                f"ASR increased {pct_change:.0f}% this month — "
                f"a regression was detected and requires immediate attention."
            )
        else:
            improvement_line = "ASR held steady — no regression detected this month."

        subject = f"RTK-1 Monthly AI Security Report — {month} | {target_model}"

        body = f"""AI Security Monthly Report — {month}
Target: {target_model}

EXECUTIVE SUMMARY
{"=" * 50}

Campaigns Run This Month: {campaigns}
Current Attack Success Rate: {current_asr}%
Month-over-Month: {framing}

{improvement_line}

{business_value}

COMPLIANCE STATUS
{"=" * 50}
EU AI Act Articles 9, 15, Annex IV: {"✅ Satisfied" if current_asr == 0 else "⚠️ Remediation Required"}
NIST AI RMF MEASURE 2.7: {"✅ Satisfied" if current_asr == 0 else "⚠️ Remediation Required"}
OWASP LLM Top 10 (LLM01): {"✅ Defended" if current_asr == 0 else f"❌ {current_asr}% bypass rate"}

WHAT THIS MEANS FOR THE BUSINESS
{"=" * 50}
{business_value if business_value else "Continuous red teaming is protecting your AI systems 24/7."}

A single AI security breach of this type could cost $5M+ in regulatory
fines, customer loss, and reputational damage. Our always-on red teaming
pipeline catches regressions before they reach production.

NEXT MONTH
{"=" * 50}
- Automated campaigns continue 24/7
- CI/CD gates active on every deployment
- Next monthly report auto-generated in 30 days

---
RTK-1 AI Red Teaming Platform
Always-on defense. Proof of safety. Every sprint.
Generated: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")}"""

        return {
            "subject": subject,
            "body": body,
            "target_model": target_model,
            "current_asr": current_asr,
            "campaigns_this_month": campaigns,
            "month": month,
        }

    # ========================
    # LINKEDIN POST (Objective 48)
    # ========================
    def generate_linkedin_post(
        self,
        target_model: str,
        goal: str,
        asr: float,
        total_sequences: int,
        job_id: str,
    ) -> str:
        """
        Auto-generates LinkedIn post from campaign results.
        Triggered after each campaign completion.
        """
        delta = history.get_asr_delta(target_model=target_model)
        pct_change = delta.get("pct_change", 0.0)
        prev_asr = delta.get("previous_asr", asr)

        if asr == 0.0:
            headline = f"Our AI red teaming pipeline just ran {total_sequences} adversarial attack sequences against {target_model} — ASR: 0%."
            insight = "Full resilience demonstrated. Every Crescendo multi-turn escalation attempt was blocked."
            cta = "This is what always-on AI security looks like."
        elif prev_asr > asr and pct_change > 10:
            headline = f"ASR dropped from {prev_asr:.0f}% to {asr:.0f}% after our latest remediation — {pct_change:.0f}% risk reduction."
            insight = f"We ran {total_sequences} adversarial attack sequences using PyRIT + Claude 4 orchestration. The numbers don't lie."
            cta = "A single breach of this type could cost $5M+. Our red teaming pipeline just saved that."
        else:
            headline = f"Latest AI red team results: {asr}% Attack Success Rate across {total_sequences} Crescendo sequences."
            insight = f"Goal: {goal[:100]}. The ReAct supervisor identified the exact attack patterns that succeed and fail."
            cta = "EU AI Act enforcement is here. Documented, quantified, continuous red teaming is no longer optional."

        return f"""{headline}

{insight}

What RTK-1 tested:
✅ {total_sequences} multi-turn Crescendo sequences
✅ Claude Sonnet 4.6 ReAct eval-driven supervisor
✅ LangGraph stateful checkpoints
✅ PyRIT 0.12.0 + customer-defined scoring
✅ EU AI Act + NIST AI RMF compliance mapping

{cta}

Report ID: RTK1-{job_id[:8].upper()}

#AIRedTeaming #LLMSecurity #EUAIAct #PromptInjection #AIGovernance #RTK1"""

    # ========================
    # ONE-CLICK DELIVERY BUNDLE (Objective 29)
    # ========================
    def generate_delivery_bundle(
        self,
        target_model: str,
        goal: str,
        asr: float,
        total_sequences: int,
        customer_success_metrics: str,
        job_id: str,
        report_link: Optional[str] = None,
        grafana_link: Optional[str] = None,
        recipient_name: str = "Team",
    ) -> dict:
        """
        One-click delivery bundle — everything the client needs.
        PDF link + executive email + slide deck + LinkedIn post +
        business value statement + monthly summary.
        """
        bvs = self.generate_business_value_statement(
            target_model, goal, asr, total_sequences, customer_success_metrics, job_id
        )
        email = self.generate_executive_email(
            target_model,
            goal,
            asr,
            total_sequences,
            customer_success_metrics,
            job_id,
            recipient_name,
            report_link,
            grafana_link,
        )
        deck = self.generate_slide_deck_content(
            target_model,
            goal,
            asr,
            total_sequences,
            customer_success_metrics,
            job_id,
            report_link,
            grafana_link,
        )
        linkedin = self.generate_linkedin_post(
            target_model, goal, asr, total_sequences, job_id
        )
        weekly = self.generate_weekly_summary_markdown(target_model)

        logger.info(
            "delivery_bundle_generated",
            job_id=job_id,
            asr=asr,
            target=target_model,
        )

        return {
            "job_id": job_id,
            "target_model": target_model,
            "asr": asr,
            "report_link": report_link,
            "grafana_link": grafana_link,
            "business_value_statement": bvs,
            "executive_email": email,
            "slide_deck": deck,
            "linkedin_post": linkedin,
            "weekly_summary": weekly,
            "generated_at": datetime.now(UTC).isoformat(),
        }


# Global singleton
delivery = DeliveryManager()
