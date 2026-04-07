"""
RTK-1 API Router — thin, clean, no business logic.
All orchestration delegated to compiled_graph via facade.
"""

import os
import sqlite3
import time
import uuid

import markdown
from fastapi import APIRouter, HTTPException
from weasyprint import HTML

from app.core.alerts import alerter
from app.core.audit import AuditEventType, audit
from app.core.config import settings
from app.core.delivery import delivery
from app.core.history import history
from app.core.logging import get_logger
from app.core.metrics import ASR_GAUGE, ATTACKS_TOTAL, LATENCY_HISTOGRAM
from app.core.rate_limiter import rate_limiter
from app.orchestrator.claude_orchestrator import compiled_graph
from app.schemas import RedTeamRequest, RedTeamResponse

logger = get_logger("redteam_router")
router = APIRouter(tags=["redteam"])


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
    if not rate_limiter.is_allowed(customer_id):
        usage = rate_limiter.get_usage(customer_id)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. {usage['remaining']} requests remaining this minute.",
        )

    try:
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

        report_link = f"{settings.base_url}/reports/{job_id}.pdf"
        grafana_link = (
            f"{settings.grafana_base_url}/d/{settings.grafana_dashboard_uid}"
            f"/rtk-1-executive-red-teaming-dashboard?var-job_id={job_id}"
        )

        await alerter.check_and_alert_asr(
            job_id=job_id,
            asr=asr,
            target_model=request.target_model,
            goal=request.goal,
            report_link=report_link,
        )

        audit.log(
            AuditEventType.CAMPAIGN_COMPLETED,
            actor="api",
            payload={"asr": asr, "latency_seconds": round(latency, 2)},
            job_id=job_id,
        )

        logger.info(
            "campaign_completed", job_id=job_id, asr=asr, latency=round(latency, 2)
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
            report_link=report_link,
            grafana_link=grafana_link,
        )

    except Exception as e:
        logger.error("campaign_failed", error=str(e))
        audit.log(
            AuditEventType.CAMPAIGN_FAILED, actor="api", payload={"error": str(e)}
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
# CI/CD GATE ENDPOINT
# ========================
@router.post("/redteam/ci")
async def run_ci_gate(request: RedTeamRequest):
    """Lightweight CI/CD gate. Returns ASR and pass/fail status."""
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
# MULTI-VECTOR ENDPOINT
# ========================
@router.post("/redteam/multi-vector")
async def run_multi_vector(
    request: RedTeamRequest,
    vectors: list[str] = None,
):
    """Multi-vector unified campaign — PyRIT + Garak + DeepTeam in parallel."""
    try:
        from app.domain.models import AttackVector, CampaignConfig
        from app.facade import facade

        config = CampaignConfig(
            target_model=request.target_model,
            goal=request.goal,
            vector=AttackVector.CRESCENDO,
            customer_success_metrics=request.customer_success_metrics,
            num_sequences=1,
            turns_per_sequence=3,
        )

        result = await facade.run_multi_vector_campaign(
            config=config,
            vectors=vectors or ["pyrit", "deepteam", "crewai"],
        )

        return {
            "campaign_id": result["campaign_id"],
            "goal": result["goal"],
            "target_model": result["target_model"],
            "vectors_run": result["vectors_run"],
            "combined_asr": result["combined_asr"],
            "per_vector_results": result["per_vector"],
            "status": "completed",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# DELIVERY BUNDLE ENDPOINT
# ========================
@router.post("/redteam/delivery-bundle")
async def get_delivery_bundle(
    request: RedTeamRequest,
    job_id: str,
    asr: float,
    total_sequences: int,
    recipient_name: str = "Team",
    customer_id: str = "default",
):
    """One-click delivery bundle — PDF + email + deck + LinkedIn + weekly summary."""
    if not rate_limiter.is_allowed(customer_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")

    try:
        report_link = f"{settings.base_url}/reports/{job_id}.pdf"
        grafana_link = (
            f"{settings.grafana_base_url}/d/{settings.grafana_dashboard_uid}"
            f"/rtk-1-executive-red-teaming-dashboard?var-job_id={job_id}"
        )

        bundle = delivery.generate_delivery_bundle(
            target_model=request.target_model,
            goal=request.goal,
            asr=asr,
            total_sequences=total_sequences,
            customer_success_metrics=request.customer_success_metrics,
            job_id=job_id,
            report_link=report_link,
            grafana_link=grafana_link,
            recipient_name=recipient_name,
        )

        return bundle

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# TREND + HISTORY ENDPOINTS
# ========================
@router.get("/redteam/trend/{target_model}")
async def get_asr_trend(target_model: str, days: int = 30):
    """ASR trend data for Grafana and executive reporting."""
    trend = history.get_asr_trend(target_model=target_model, days=days)
    delta = history.get_asr_delta(target_model=target_model)
    return {"target_model": target_model, "days": days, "trend": trend, "delta": delta}


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


@router.get("/redteam/delta/{target_model}")
async def get_asr_delta(target_model: str):
    """Week-over-week ASR delta with business value framing."""
    return history.get_asr_delta(target_model=target_model)


@router.get("/redteam/weekly-summary/{target_model}")
async def get_weekly_summary(target_model: str, days: int = 7):
    """Weekly summary markdown for executive reporting."""
    summary = delivery.generate_weekly_summary_markdown(
        target_model=target_model, days=days
    )
    return {"target_model": target_model, "summary": summary}


@router.get("/redteam/monthly-report/{target_model}")
async def get_monthly_report(target_model: str):
    """Monthly executive dashboard email content."""
    return delivery.generate_monthly_executive_email(target_model=target_model)


@router.get("/redteam/rate-limit/{customer_id}")
async def get_rate_limit_status(customer_id: str):
    """Check rate limit status for a customer."""
    return rate_limiter.get_usage(customer_id)


# ========================
# COMPARE MODELS ENDPOINT
# ========================
@router.post("/redteam/compare")
async def compare_models(
    target_models: list[str],
    goal: str,
    customer_success_metrics: str = "Compare robustness across model variants",
):
    """Run same campaign against multiple models in parallel."""
    try:
        from app.domain.models import AttackVector, CampaignConfig
        from app.facade import facade

        configs = [
            CampaignConfig(
                target_model=model,
                goal=goal,
                vector=AttackVector.CRESCENDO,
                customer_success_metrics=customer_success_metrics,
                num_sequences=1,
                turns_per_sequence=3,
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
# FEDERATED + ATTACK LIBRARY ENDPOINTS
# ========================
@router.post("/redteam/federated")
async def run_federated_campaign(
    request: RedTeamRequest,
    node_urls: list[str] = None,
):
    """
    Federated red teaming — coordinate attacks from multiple nodes.
    Tests rate limiting, geo-blocking, and anomaly detection.
    """
    try:
        from app.core.federated import coordinator
        from app.domain.models import AttackVector, CampaignConfig

        if node_urls:
            for url in node_urls:
                coordinator.register_node(url)

        config = CampaignConfig(
            target_model=request.target_model,
            goal=request.goal,
            vector=AttackVector.CRESCENDO,
            customer_success_metrics=request.customer_success_metrics,
            num_sequences=1,
            turns_per_sequence=3,
        )

        result = await coordinator.run_federated_campaign(config)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/redteam/attack-library")
async def get_attack_library():
    """Return all known attack techniques in the library."""
    from app.core.attack_library import attack_library

    return {
        "techniques": attack_library.get_all_techniques(),
        "total": len(attack_library.get_all_techniques()),
    }


@router.get("/redteam/attack-library/{owasp_category}")
async def get_techniques_by_owasp(owasp_category: str):
    """Return attack techniques filtered by OWASP LLM category."""
    from app.core.attack_library import attack_library

    techniques = attack_library.get_techniques_by_owasp(owasp_category)
    return {
        "owasp_category": owasp_category,
        "techniques": techniques,
        "total": len(techniques),
    }


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
