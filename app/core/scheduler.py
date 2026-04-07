"""
RTK-1 Campaign Scheduler — runs campaigns on a configurable schedule.
Enables continuous 24/7 red teaming without human intervention.
"""

import asyncio
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("scheduler")


class CampaignScheduler:
    """
    Runs RTK-1 campaigns on a schedule.
    Designed to run as a background task in the FastAPI lifespan.
    """

    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if not settings.scheduled_campaign_enabled:
            logger.info("scheduler_disabled", reason="SCHEDULED_CAMPAIGN_ENABLED=false")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            "scheduler_started",
            cron=settings.scheduled_campaign_cron,
            target=settings.scheduled_target_model,
        )

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            logger.info("scheduler_stopped")

    async def _run_loop(self) -> None:
        """Simple interval-based scheduler. Replace with APScheduler for cron support."""
        interval_seconds = 86400  # 24 hours default

        while self._running:
            try:
                logger.info("scheduled_campaign_starting")
                await self._run_scheduled_campaign()
                logger.info("scheduled_campaign_completed")
            except Exception as e:
                logger.error("scheduled_campaign_failed", error=str(e))

            await asyncio.sleep(interval_seconds)

    async def _run_scheduled_campaign(self) -> None:
        """Import here to avoid circular imports at module load."""
        import uuid

        from app.core.alerts import alerter
        from app.core.history import history
        from app.orchestrator.claude_orchestrator import compiled_graph

        job_id_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

        result = await compiled_graph.ainvoke(
            {
                "target_model": settings.scheduled_target_model,
                "goal": settings.scheduled_goal,
                "attack_type": "crescendo",
                "customer_success_metrics": settings.scheduled_customer_metrics,
            },
            job_id_config,
        )

        asr = result.get("asr", 0.0)
        job_id = result.get("job_id", "unknown")

        history.save_campaign(
            job_id=job_id,
            campaign_id=job_id,
            target_model=settings.scheduled_target_model,
            goal=settings.scheduled_goal,
            attack_type="crescendo",
            customer_success_metrics=settings.scheduled_customer_metrics,
            total_sequences=result.get("sequences_run", 0),
            successful_sequences=int(result.get("sequences_run", 0) * asr / 100),
            asr=asr,
            robustness_rating="auto-scheduled",
        )

        await alerter.check_and_alert_asr(
            job_id=job_id,
            asr=asr,
            target_model=settings.scheduled_target_model,
            goal=settings.scheduled_goal,
        )

        logger.info("scheduled_campaign_saved", job_id=job_id, asr=asr)


# Global singleton
scheduler = CampaignScheduler()
