"""
RTK-1 Alerting — Slack webhooks on ASR spikes and campaign events.
"""

from typing import Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("alerts")


class AlertManager:
    async def send_slack(self, message: str, urgent: bool = False) -> bool:
        if not settings.slack_webhook_url:
            logger.info("slack_skipped", reason="no webhook configured")
            return False

        icon = "🚨" if urgent else "📊"
        payload = {
            "text": f"{icon} *RTK-1 Alert*",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{icon} *RTK-1 Alert*\n{message}",
                    },
                }
            ],
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    settings.slack_webhook_url,
                    json=payload,
                    timeout=10,
                )
            if resp.status_code == 200:
                logger.info("slack_sent", urgent=urgent)
                return True
            else:
                logger.warning("slack_failed", status=resp.status_code)
                return False
        except Exception as e:
            logger.error("slack_error", error=str(e))
            return False

    async def check_and_alert_asr(
        self,
        job_id: str,
        asr: float,
        target_model: str,
        goal: str,
        report_link: Optional[str] = None,
    ) -> None:
        if asr >= settings.asr_spike_threshold:
            message = (
                f"*ASR Spike Detected*\n"
                f"Job: `{job_id}`\n"
                f"Model: `{target_model}`\n"
                f"Goal: {goal}\n"
                f"ASR: *{asr}%* (threshold: {settings.asr_spike_threshold}%)\n"
                f"{'Report: ' + report_link if report_link else ''}\n"
                f"Immediate human review required."
            )
            await self.send_slack(message, urgent=True)
            logger.warning(
                "asr_spike",
                job_id=job_id,
                asr=asr,
                threshold=settings.asr_spike_threshold,
            )


# Global singleton
alerter = AlertManager()
