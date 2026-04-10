"""
RTK-1 API Router — thin, clean, no business logic.
All orchestration delegated to compiled_graph via facade.
"""

import os
import sqlite3
import time
import uuid
from typing import Optional

import markdown
from fastapi import APIRouter, HTTPException
from weasyprint import HTML

from app.core.alerts import alerter
from app.core.audit import AuditEventType, audit
from app.core.config import settings
from app.core.history import history
from app.core.logging import get_logger
from app.core.metrics import ASR_GAUGE, ATTACKS_TOTAL, LATENCY_HISTOGRAM
from app.orchestrator.claude_orchestrator import compiled_graph
from app.schemas import RedTeamRequest, RedTeamResponse

logger = get_logger("redteam_router")
router = APIRouter(tags=["redteam"])


# ========================
# HELPERS
# ========================


def generate_pdf_report(markdown_content: str, job_id: str) -> str:
    html_content = markdown.markdown(
        markdown_content,
        extensions=["tables", "fenced_code"],
    )
    os.makedirs("reports", exist_ok=True)
    pdf_path = f"reports/{job_id}.pdf"
    HTML(string=html_content).write_pdf(pdf_path)
    return pdf_path


async def _invoke_graph(request: RedTeamRequest) -> dict:
    """Shared graph invocation used by all endpoints."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    return await compiled_graph.ainvoke(
        {
            "target_model": request.target_model,
            "goal": request.goal,
            "attack_type": request.attack_type,
            "customer_success_metrics": request.customer_success_metrics,
        },
        config,
    )


# ========================
# MAIN CAMPAIGN ENDPOINT
# ========================


@router.post("/redteam/crescendo-with-report", response_model=RedTeamResponse)
async def run_crescendo_with_report(
    request: RedTeamRequest,
    customer_id: str = "default",
):
    """
    Run a full Crescendo red team campaign.
    Returns PDF report + Grafana link + compliance mapping.
    """
    try:
        # Per-customer rate limiting
        from app.core.rate_limiter import rate_limiter

        limit_check = rate_limiter.check_and_increment(
            customer_id=customer_id,
            max_requests=settings.rate_limit_max_requests,
            window_seconds=settings.rate_limit_window_seconds,
        )
        if not limit_check["allowed"]:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Rate limit exceeded. "
                    f"{limit_check['requests_remaining']} requests remaining "
                    f"in current window."
                ),
            )

        ATTACKS_TOTAL.inc()
        start_time = time.time()

        audit.log(
            AuditEventType.CAMPAIGN_STARTED,
            actor="api",
            payload={
                "target_model": request.target_model,
                "goal": request.goal,
                "attack_type": request.attack_type,
                "customer_id": customer_id,
            },
        )

        result = await _invoke_graph(request)

        latency = time.time() - start_time
        LATENCY_HISTOGRAM.observe(latency)
        asr = result.get("asr", 0.0)
        ASR_GAUGE.set(asr)

        job_id = result["job_id"]
        generate_pdf_report(result["final_report_markdown"], job_id)

        await alerter.check_and_alert_asr(
            job_id=job_id,
            asr=asr,
            target_model=request.target_model,
            goal=request.goal,
            report_link=f"{settings.base_url}/reports/{job_id}.pdf",
        )

        audit.log(
            AuditEventType.CAMPAIGN_COMPLETED,
            actor="api",
            payload={"asr": asr, "latency_seconds": round(latency, 2)},
            job_id=job_id,
        )

        logger.info(
            "campaign_completed",
            job_id=job_id,
            asr=asr,
            latency=round(latency, 2),
        )

        return RedTeamResponse(
            job_id=job_id,
            status="completed",
            attack_type=request.attack_type,
            total_sequences=result.get("sequences_run", 0),
            sequences_run=result.get("sequences_run", 0),
            asr=asr,
            results=result.get("results"),
            final_report_markdown=result["final_report_markdown"],
            report_link=f"{settings.base_url}/reports/{job_id}.pdf",
            grafana_link=(
                f"{settings.grafana_base_url}/d/{settings.grafana_dashboard_uid}"
                f"/rtk-1-executive-red-teaming-dashboard?var-job_id={job_id}"
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("campaign_failed", error=str(e))
        audit.log(
            AuditEventType.CAMPAIGN_FAILED,
            actor="api",
            payload={"error": str(e)},
        )
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# LIGHTWEIGHT ENDPOINT
# ========================


@router.post("/redteam/crescendo")
async def run_crescendo(request: RedTeamRequest):
    """Lightweight endpoint — raw result without PDF generation."""
    try:
        result = await _invoke_graph(request)
        return {
            "job_id": result["job_id"],
            "asr": result.get("asr", 0.0),
            "sequences_run": result.get("sequences_run", 0),
            "status": "completed",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# CI/CD GATE ENDPOINT (Objective 23)
# ========================


@router.post("/redteam/ci")
async def run_ci_gate(request: RedTeamRequest):
    """
    Lightweight CI/CD gate endpoint.
    Returns ASR and pass/fail status. Fails fast, no PDF generation.
    """
    try:
        ATTACKS_TOTAL.inc()

        result = await _invoke_graph(request)

        asr = result.get("asr", 0.0)
        job_id = result["job_id"]
        passed = asr < settings.ci_fail_on_asr_above

        audit.log(
            AuditEventType.CI_GATE_PASSED if passed else AuditEventType.CI_GATE_FAILED,
            actor="ci_pipeline",
            payload={"asr": asr, "threshold": settings.ci_fail_on_asr_above},
            job_id=job_id,
        )

        await alerter.check_and_alert_asr(
            job_id=job_id,
            asr=asr,
            target_model=request.target_model,
            goal=request.goal,
        )

        logger.info("ci_gate_evaluated", job_id=job_id, asr=asr, passed=passed)

        return {
            "job_id": job_id,
            "asr": asr,
            "passed": passed,
            "threshold": settings.ci_fail_on_asr_above,
            "status": "passed" if passed else "failed",
            "message": (
                f"ASR {asr}% "
                f"{'within' if passed else 'exceeds'} "
                f"threshold {settings.ci_fail_on_asr_above}%"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# TREND + HISTORY (Objective 20)
# ========================


@router.get("/redteam/trend/{target_model}")
async def get_asr_trend(target_model: str, days: int = 30):
    """ASR trend data for Grafana and executive reporting."""
    trend = history.get_asr_trend(target_model=target_model, days=days)
    delta = history.get_asr_delta(target_model=target_model)
    return {
        "target_model": target_model,
        "days": days,
        "trend": trend,
        "delta": delta,
    }


@router.get("/redteam/history")
async def get_campaign_history(limit: int = 20):
    """Recent campaign history for dashboard."""
    with sqlite3.connect(settings.campaign_db_path) as conn:
        rows = conn.execute(
            """
            SELECT job_id, target_model, asr, robustness_rating,
                   completed_at, git_commit
            FROM campaigns ORDER BY completed_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "job_id": r[0],
            "target_model": r[1],
            "asr": r[2],
            "robustness_rating": r[3],
            "completed_at": r[4],
            "git_commit": r[5],
        }
        for r in rows
    ]


# ========================
# DELTA / BUSINESS VALUE (Objective 21)
# ========================


@router.get("/redteam/delta/{target_model}")
async def get_asr_delta(target_model: str):
    """
    Week-over-week ASR delta with business value framing.
    Powers the '93% safer' executive narrative.
    """
    delta = history.get_asr_delta(target_model=target_model)
    return delta


# ========================
# MULTI-MODEL COMPARISON (Objective 57)
# ========================


@router.post("/redteam/compare")
async def compare_models(
    target_models: list[str],
    goal: str,
    customer_success_metrics: str = "Compare robustness across model variants",
):
    """
    Run the same campaign against multiple models in parallel.
    Returns comparative ASR report.
    """
    try:
        from app.domain.models import AttackVector, CampaignConfig
        from app.facade import facade

        configs = [
            CampaignConfig(
                target_model=model,
                goal=goal,
                vector=AttackVector.CRESCENDO,
                customer_success_metrics=customer_success_metrics,
                num_sequences=3,
                turns_per_sequence=8,
            )
            for model in target_models
        ]

        results = await facade.run_parallel_campaigns(configs)

        comparison = [
            {
                "target_model": r.target_model,
                "asr": r.asr,
                "total_sequences": r.total_sequences,
                "successful_sequences": r.successful_sequences,
                "status": r.status,
            }
            for r in results
        ]

        comparison.sort(key=lambda x: x["asr"])

        return {
            "goal": goal,
            "models_compared": len(comparison),
            "safest_model": comparison[0]["target_model"] if comparison else None,
            "most_vulnerable": comparison[-1]["target_model"] if comparison else None,
            "comparison": comparison,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# MULTI-VECTOR ENDPOINT (Objective 19)
# ========================


@router.post("/redteam/multi-vector")
async def run_multi_vector(request: RedTeamRequest):
    """
    Run PyRIT + RAG injection + tool abuse in parallel.
    Returns unified ASR with per-vector breakdown.
    Ideal for A2SPA validation and full agentic stack testing.
    """
    try:
        from langchain_anthropic import ChatAnthropic

        from app.domain.models import AttackVector, CampaignConfig
        from app.providers.multi_vector_provider import MultiVectorProvider
        from app.providers.scorer_generator import ScorerGenerator

        llm = ChatAnthropic(
            model=settings.default_model,
            temperature=0.7,
            max_tokens=4096,
            anthropic_api_key=settings.anthropic_api_key,
        )

        provider = MultiVectorProvider(llm=llm)

        config = CampaignConfig(
            target_model=request.target_model,
            goal=request.goal,
            vector=AttackVector.CRESCENDO,
            customer_success_metrics=request.customer_success_metrics,
            num_sequences=3,
            turns_per_sequence=5,
        )

        scorer_gen = ScorerGenerator(llm=llm)
        scorer_config = await scorer_gen.generate(
            goal=request.goal,
            customer_success_metrics=request.customer_success_metrics,
            target_model=request.target_model,
        )

        results = await provider.run_campaign(config, scorer_config)

        total = len(results)
        successful = sum(1 for r in results if r.success)
        asr = round((successful / total) * 100, 2) if total > 0 else 0.0

        breakdown = {}
        for tool_name in ["pyrit", "rag_injection", "tool_abuse"]:
            vector_results = [
                r
                for r in results
                if hasattr(r, "attack_tool") and r.attack_tool.value == tool_name
            ]
            if vector_results:
                v_successful = sum(1 for r in vector_results if r.success)
                breakdown[tool_name] = {
                    "total": len(vector_results),
                    "successful": v_successful,
                    "asr": round((v_successful / len(vector_results)) * 100, 2),
                }

        return {
            "job_id": str(uuid.uuid4()),
            "target_model": request.target_model,
            "goal": request.goal,
            "total_sequences": total,
            "successful_sequences": successful,
            "overall_asr": asr,
            "vector_breakdown": breakdown,
            "status": "completed",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# DELIVERY BUNDLE (Objective 29)
# ========================


@router.post("/redteam/delivery-bundle")
async def get_delivery_bundle(
    job_id: str,
    target_model: str,
    asr: float,
    goal: str,
    total_sequences: int = 0,
    successful_sequences: int = 0,
    customer_success_metrics: str = "",
    previous_asr: Optional[float] = None,
    customer_name: str = "Team",
):
    """
    One-click delivery bundle — all content generated from campaign data.
    Business value statement + executive email + slide deck + LinkedIn post.
    """
    try:
        from app.core.delivery import delivery

        report_link = f"{settings.base_url}/reports/{job_id}.pdf"
        bundle = delivery.delivery_bundle(
            job_id=job_id,
            target_model=target_model,
            asr=asr,
            goal=goal,
            total_sequences=total_sequences,
            successful_sequences=successful_sequences,
            customer_success_metrics=customer_success_metrics,
            previous_asr=previous_asr,
            customer_name=customer_name,
            report_link=report_link,
        )
        return bundle
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/redteam/weekly-summary/{target_model}")
async def get_weekly_summary(target_model: str):
    """Weekly PDF summary markdown for auto-generation."""
    try:
        from app.core.delivery import delivery

        return {"summary": delivery.weekly_summary_markdown(target_model)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/redteam/monthly-report/{target_model}")
async def get_monthly_report(target_model: str, customer_name: str = "Team"):
    """Monthly executive dashboard email."""
    try:
        from app.core.delivery import delivery

        return delivery.monthly_executive_email(target_model, customer_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# RATE LIMIT STATUS (Objective 27)
# ========================


@router.get("/redteam/rate-limit/{customer_id}")
async def get_rate_limit_status(customer_id: str):
    """Per-customer rate limit status."""
    try:
        from app.core.rate_limiter import rate_limiter

        return rate_limiter.get_status(customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# SALES ENDPOINT (stub)
# ========================


@router.post("/sales/run")
async def run_agentic_sales():
    try:
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        result = await compiled_graph.ainvoke({"task": "run_sales_engine"}, config)
        return {
            "status": "completed",
            "leads_found": result.get("icp"),
            "qualified_leads": result.get("qualification_rubric"),
            "personalized_outreach": result.get("message_templates"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
