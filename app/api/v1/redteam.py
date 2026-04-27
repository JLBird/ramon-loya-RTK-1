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


# ========================
# VDP DISCLOSURE PACKAGE (Objective 69)
# ========================


@router.post("/redteam/vdp-package")
async def create_vdp_package(
    job_id: str,
    target_model: str,
    attack_type: str,
    asr: float,
    system_scope: str = "AI language model — production deployment",
    asset_criticality: str = "HIGH",
    output_format: str = "json",  # "json" | "xml"
):
    """
    Generate VDP-ready DHS AI-ISAC disclosure package.
    NDAA Section 1512 compliant. Supports JSON (v1.0) and XML (v1.1).
    """
    try:
        from app.core.isac_transporter import isac_transporter

        # Pull results from campaign history if available
        results = []
        try:
            import sqlite3

            with sqlite3.connect(settings.campaign_db_path) as conn:
                rows = conn.execute(
                    "SELECT results_json FROM campaigns WHERE job_id=?", (job_id,)
                ).fetchone()
            if rows and rows[0]:
                import json

                results = json.loads(rows[0])
        except Exception:
            pass

        payload = isac_transporter.build_payload(
            job_id=job_id,
            target_model=target_model,
            attack_type=attack_type,
            asr=asr,
            results=results,
            system_scope=system_scope,
            asset_criticality=asset_criticality,
        )

        if output_format == "xml":
            return {
                "job_id": job_id,
                "format": "xml",
                "schema_version": "1.1",
                "content": isac_transporter.to_xml(payload),
                "ndaa_1512_compliant": True,
            }

        return {
            "job_id": job_id,
            "format": "json",
            "schema_version": "1.0",
            "payload": payload.model_dump(),
            "ndaa_1512_compliant": True,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/redteam/vdp-package/{job_id}")
async def get_vdp_package(job_id: str, output_format: str = "json"):
    """Retrieve existing VDP package for a completed campaign."""
    try:
        import sqlite3

        from app.core.isac_transporter import isac_transporter

        with sqlite3.connect(settings.campaign_db_path) as conn:
            row = conn.execute(
                "SELECT target_model, asr FROM campaigns WHERE job_id=?", (job_id,)
            ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"Campaign {job_id} not found")

        payload = isac_transporter.build_payload(
            job_id=job_id,
            target_model=row[0],
            attack_type="crescendo",
            asr=row[1],
            results=[],
        )

        return {
            "job_id": job_id,
            "format": output_format,
            "payload": payload.model_dump(),
            "ndaa_1512_compliant": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# REPORT SIGNING + VERIFY (Objective 68)
# ========================


@router.post("/redteam/sign/{job_id}")
async def sign_report(job_id: str):
    """
    SHA-256 sign a completed report for FCA liability protection.
    Returns signature record with HMAC for tamper detection.
    """
    try:
        import os

        from app.core.report_signer import report_signer

        report_path = f"reports/{job_id}.pdf"
        md_path = f"reports/{job_id}.md"

        content = ""
        for path in [md_path, report_path]:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    content = f.read().decode("utf-8", errors="ignore")
                break

        if not content:
            raise HTTPException(
                status_code=404, detail=f"No report found for job_id {job_id}"
            )

        record = report_signer.sign(job_id=job_id, report_markdown=content)

        return {
            "job_id": job_id,
            "signature_id": record.signature_id,
            "report_sha256": record.report_sha256,
            "hmac_signature": record.hmac_signature[:16] + "...",
            "signed_at": record.signed_at.isoformat(),
            "fca_compliant": record.fca_compliant,
            "ndaa_1512_compliant": record.ndaa_1512_compliant,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/redteam/verify/{job_id}")
async def verify_report(job_id: str):
    """Verify report integrity against stored SHA-256 signature."""
    try:
        import os

        from app.core.report_signer import report_signer

        content = ""
        for path in [f"reports/{job_id}.md", f"reports/{job_id}.pdf"]:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    content = f.read().decode("utf-8", errors="ignore")
                break

        if not content:
            raise HTTPException(
                status_code=404, detail=f"No report found for job_id {job_id}"
            )

        return report_signer.verify(job_id=job_id, report_markdown=content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# BLAST RADIUS / REMEDIATION (Objectives 78, 79)
# ========================


@router.post("/redteam/remediation-impact")
async def get_remediation_impact(
    job_id: str,
    proposed_patch: str,
    target_model: str,
    original_asr: float,
):
    """
    Evaluate impact of a proposed patch against known attack prompts.
    Returns blast_radius_score + patch_confidence + re-test results.
    ITIL 4: Change Control → Risk Assessment → Validation.
    """
    try:
        from app.core.blast_radius import PatchProposal, blast_radius_engine

        patch = PatchProposal(
            job_id=job_id,
            vulnerability_summary=f"Identified via RTK-1 campaign — ASR: {original_asr}%",
            proposed_patch=proposed_patch,
            patch_type="system_prompt",
        )

        result = await blast_radius_engine.evaluate_patch(
            job_id=job_id,
            patch=patch,
            original_asr=original_asr,
            successful_prompts=[],
            target_model=target_model,
        )

        return {
            "job_id": job_id,
            "original_asr": result.original_asr,
            "post_patch_asr": result.post_patch_asr,
            "asr_reduction": result.asr_reduction,
            "patch_verified": result.patch_verified,
            "patch_confidence": result.patch_confidence,
            "blast_radius_score": result.production_impact_score,
            "remediation_impact_score": result.remediation_impact_score,
            "itil4_change_risk": result.itil4_change_risk,
            "summary": result.summary,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# NEUTRALITY CHECK (Objective 71)
# ========================


@router.post("/redteam/neutrality-check")
async def run_neutrality_check(
    target_model: str = "claude-sonnet-4-6",
    customer_id: str = "default",
):
    """
    GSA federal procurement neutrality check.
    Tests for political bias, sycophancy, and factual accuracy under pressure.
    Returns Neutrality Score (0-100) + GSA compliance status.
    """
    try:
        from app.providers.neutrality_provider import NeutralityProvider

        provider = NeutralityProvider()
        report = await provider.run_neutrality_check(target_model=target_model)

        return {
            "target_model": target_model,
            "neutrality_score": report.neutrality_score,
            "ideological_score": report.ideological_score,
            "sycophancy_score": report.sycophancy_score,
            "factual_pressure_score": report.factual_pressure_score,
            "gsa_compliant": report.gsа_compliant,
            "tests_run": report.tests_run,
            "tests_failed": report.tests_failed,
            "summary": report.summary,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# RIYADH CHARTER COMPLIANCE REPORT (Objective ME-01)
# ========================


@router.post("/redteam/riyadh-compliance-report")
async def run_riyadh_compliance_report(
    request: RedTeamRequest,
    customer_id: str = "default",
    sovereign_hosting_mode: Optional[
        str
    ] = None,  # "private_hub" | "extended_hub" | "virtual_hub"
    bilingual_delivery: bool = False,
):
    """
    Middle East & Islamic World compliance report.

    Orchestrates a Crescendo campaign + runs NeutralityProvider with
    islamic_values=True + applies the Riyadh Charter / SDAIA / MOAI / DIFC /
    ADGM / ALECSO / KSA+UAE PDPL / ISO 42001 mapping.

    Returns a single signed evidence package suitable for vendor qualification
    in Saudi Arabia (SDAIA Self-Assessment), the UAE (MOAI AI Seal), DIFC,
    ADGM, and the broader 53-state ICESCO membership.
    """
    try:
        from app.core.compliance_riyadh import compliance_riyadh_mapper
        from app.providers.neutrality_provider import NeutralityProvider

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
                "endpoint": "riyadh-compliance-report",
                "sovereign_hosting_mode": sovereign_hosting_mode,
                "bilingual_delivery": bilingual_delivery,
            },
        )

        # 1. Run the Crescendo campaign via the orchestrator graph
        campaign_result = await _invoke_graph(request)
        job_id = campaign_result["job_id"]
        overall_asr = campaign_result.get("asr", 0.0)

        latency = time.time() - start_time
        LATENCY_HISTOGRAM.observe(latency)
        ASR_GAUGE.set(overall_asr)

        # 2. Run NeutralityProvider with islamic_values layer enabled
        neutrality_provider = NeutralityProvider()
        neutrality_report = await neutrality_provider.run_neutrality_check(
            target_model=request.target_model,
            islamic_values=True,
        )

        # 3. Apply the Riyadh Charter mapping
        # Tools exercised in this campaign:
        # - "pyrit" (crescendo via _invoke_graph)
        # - "neutrality" + "islamic_values" (this endpoint always runs both)
        tools_exercised = ["pyrit", "neutrality", "islamic_values"]

        riyadh_report = compliance_riyadh_mapper.map_campaign_to_riyadh(
            job_id=job_id,
            target_model=request.target_model,
            tools_exercised=tools_exercised,
            overall_asr=overall_asr,
            islamic_values_score=neutrality_report.islamic_values_score,
            sovereign_hosting_mode=sovereign_hosting_mode,
            bilingual_delivery=bilingual_delivery,
        )

        # 4. Generate companion pre-fill packages
        sdaia_prefill = compliance_riyadh_mapper.map_to_sdaia_self_assessment(
            target_model=request.target_model,
            overall_asr=overall_asr,
            tools_exercised=tools_exercised,
        )
        moai_prefill = compliance_riyadh_mapper.map_to_moai_seal(
            target_model=request.target_model,
            overall_asr=overall_asr,
            tools_exercised=tools_exercised,
        )

        audit.log(
            AuditEventType.CAMPAIGN_COMPLETED,
            actor="api",
            payload={
                "asr": overall_asr,
                "riyadh_compliant": riyadh_report.riyadh_compliant,
                "principles_exercised": riyadh_report.principles_exercised,
                "islamic_values_score": neutrality_report.islamic_values_score,
                "latency_seconds": round(latency, 2),
            },
            job_id=job_id,
        )

        logger.info(
            "riyadh_compliance_report_completed",
            job_id=job_id,
            asr=overall_asr,
            riyadh_compliant=riyadh_report.riyadh_compliant,
            principles_exercised=riyadh_report.principles_exercised,
            islamic_values_score=neutrality_report.islamic_values_score,
            sovereign_hosting_mode=sovereign_hosting_mode,
        )

        return {
            "job_id": job_id,
            "target_model": request.target_model,
            "goal": request.goal,
            "overall_asr": overall_asr,
            "c2_pass": riyadh_report.c2_pass,
            "riyadh_compliant": riyadh_report.riyadh_compliant,
            "principles_exercised": riyadh_report.principles_exercised,
            "principles": [p.model_dump() for p in riyadh_report.principles],
            "frameworks": [f.model_dump() for f in riyadh_report.frameworks],
            "sdaia_self_assessment_prefill_pct": riyadh_report.sdaia_self_assessment_prefill_pct,
            "moai_seal_prefill_pct": riyadh_report.moai_seal_prefill_pct,
            "sovereign_hosting_mode": riyadh_report.sovereign_hosting_mode,
            "bilingual_delivery_available": riyadh_report.bilingual_delivery_available,
            "neutrality_summary": {
                "neutrality_score": neutrality_report.neutrality_score,
                "gsa_compliant": neutrality_report.gsа_compliant,
                "islamic_values_score": neutrality_report.islamic_values_score,
                "islamic_values_failed": neutrality_report.islamic_values_failed,
                "tests_run": neutrality_report.tests_run,
                "tests_failed": neutrality_report.tests_failed,
            },
            "sdaia_self_assessment_prefill": sdaia_prefill,
            "moai_seal_prefill": moai_prefill,
            "summary": riyadh_report.summary,
            "report_link": f"{settings.base_url}/reports/{job_id}.pdf",
            "status": "completed",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("riyadh_compliance_report_failed", error=str(e))
        audit.log(
            AuditEventType.CAMPAIGN_FAILED,
            actor="api",
            payload={"error": str(e), "endpoint": "riyadh-compliance-report"},
        )
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# DUAL MODEL VALIDATION (Objective 76)
# ========================


@router.post("/redteam/dual-validate")
async def dual_validate(
    job_id: str,
    goal: str,
    target_model: str,
    attack_prompt: str = None,
):
    """
    Claude 4 proposes attack → secondary model predicts blast radius.
    Returns attack_success_probability + blast_radius_score + combined_risk.
    """
    try:
        from app.core.continual_monitor import dual_model_validator

        result = await dual_model_validator.validate(
            job_id=job_id,
            goal=goal,
            target_model=target_model,
            attack_prompt=attack_prompt,
        )

        return {
            "validation_id": result.validation_id,
            "job_id": job_id,
            "attack_success_probability": result.attack_success_probability,
            "blast_radius_score": result.blast_radius_score,
            "combined_risk_score": result.combined_risk_score,
            "recommendation": result.recommendation,
            "defender_assessment": result.defender_assessment[:300],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# SUBSCRIPTION STATUS (Objective 83)
# ========================


@router.get("/subscriptions/{customer_id}")
async def get_subscription_status(customer_id: str):
    """Get subscription tier, limits, and campaign usage."""
    try:
        from app.core.subscription import subscription_manager

        sub = subscription_manager.get_subscription(customer_id)
        if not sub:
            raise HTTPException(
                status_code=404, detail=f"No subscription for {customer_id}"
            )

        check = subscription_manager.check_campaign_allowed(customer_id)
        limits = subscription_manager.get_tier_info(sub.tier)

        return {
            "customer_id": customer_id,
            "tier": sub.tier.value,
            "active": sub.active,
            "campaigns_this_month": sub.campaigns_this_month,
            "campaigns_remaining": check.get("remaining", -1),
            "campaign_allowed": check["allowed"],
            "limits": limits,
            "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# CIR DASHBOARD (Objective 91)
# ========================


@router.get("/itil/cir")
async def get_cir_dashboard():
    """ITIL 4 Continual Improvement Register dashboard."""
    try:
        from app.core.cir import cir

        return cir.get_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/itil/cir/entries")
async def get_cir_entries(status: str = None):
    """Get all CIR entries, optionally filtered by status."""
    try:
        from app.core.cir import CIRStatus, cir

        s = CIRStatus(status) if status else None
        return {"entries": cir.get_all(status=s)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# SOCIAL AUTO-POST (Objectives 93, 94, 95)
# ========================


@router.post("/social/post-campaign")
async def post_campaign_to_social(
    asr: float,
    target_model: str,
    goal: str,
    dry_run: bool = False,
):
    """
    Auto-post campaign results to X and LinkedIn.
    Set dry_run=True to preview without publishing.
    SEO keywords injected automatically.
    """
    try:
        from app.core.social_automation import profile_sync

        result = await profile_sync.sync_on_campaign_milestone(
            asr=asr,
            target_model=target_model,
            goal=goal,
            trigger="api_triggered",
            dry_run=dry_run,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/social/post-custom")
async def post_custom_to_social(
    x_template: str = "technical_insight",
    li_template: str = "enterprise_win",
    asr: float = 0.0,
    target_model: str = "claude-sonnet-4-6",
    goal: str = "AI red teaming campaign",
    dry_run: bool = False,
):
    """
    Post with explicitly chosen templates.
    x_template options: technical_insight, compliance_win, security_research, asr_improvement
    li_template options: enterprise_win, asr_improvement, new_provider, regulatory_milestone, research_finding
    """
    try:
        from app.core.social_automation import profile_sync

        context = {
            "asr": asr,
            "target_model": target_model,
            "goal": goal[:100],
            "platform": "RTK-1 autonomous AI red teaming platform",
        }
        result = await profile_sync.post_custom(
            x_template=x_template,
            li_template=li_template,
            context=context,
            dry_run=dry_run,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
