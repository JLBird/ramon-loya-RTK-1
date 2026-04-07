"""
RTK-1 Campaign History — persists every completed campaign.
Powers ASR trend tracking, week-over-week delta, and risk dashboard.
"""

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("history")


class CampaignHistory:
    """Persistent campaign store for trend analysis and reporting."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.campaign_db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    campaign_id TEXT NOT NULL,
                    target_model TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    attack_type TEXT NOT NULL,
                    customer_success_metrics TEXT,
                    total_sequences INTEGER NOT NULL,
                    successful_sequences INTEGER NOT NULL,
                    asr REAL NOT NULL,
                    robustness_rating TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    report_path TEXT,
                    git_commit TEXT,
                    results_json TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_completed_at
                ON campaigns(completed_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_target_model
                ON campaigns(target_model)
            """)
            conn.commit()

    def save_campaign(
        self,
        job_id: str,
        campaign_id: str,
        target_model: str,
        goal: str,
        attack_type: str,
        customer_success_metrics: str,
        total_sequences: int,
        successful_sequences: int,
        asr: float,
        robustness_rating: str,
        report_path: Optional[str] = None,
        results: Optional[List[Dict]] = None,
    ) -> None:
        import subprocess

        try:
            git_commit = (
                subprocess
                .check_output(
                    ["git", "rev-parse", "--short", "HEAD"],
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
        except Exception:
            git_commit = "unknown"

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO campaigns
                (job_id, campaign_id, target_model, goal, attack_type,
                 customer_success_metrics, total_sequences, successful_sequences,
                 asr, robustness_rating, completed_at, environment,
                 report_path, git_commit, results_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    campaign_id,
                    target_model,
                    goal,
                    attack_type,
                    customer_success_metrics,
                    total_sequences,
                    successful_sequences,
                    asr,
                    robustness_rating,
                    datetime.now(UTC).isoformat(),
                    settings.environment,
                    report_path,
                    git_commit,
                    json.dumps(results or []),
                ),
            )
            conn.commit()

        logger.info(
            "campaign_saved",
            job_id=job_id,
            asr=asr,
            git_commit=git_commit,
        )

    def get_asr_trend(
        self,
        target_model: str,
        days: int = 30,
        goal: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get ASR over time for trend analysis."""
        since = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        query = """
            SELECT job_id, asr, robustness_rating, completed_at, git_commit
            FROM campaigns
            WHERE target_model = ? AND completed_at >= ?
        """
        params = [target_model, since]
        if goal:
            query += " AND goal = ?"
            params.append(goal)
        query += " ORDER BY completed_at ASC"

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()

        return [
            {
                "job_id": r[0],
                "asr": r[1],
                "robustness_rating": r[2],
                "completed_at": r[3],
                "git_commit": r[4],
            }
            for r in rows
        ]

    def get_asr_delta(
        self,
        target_model: str,
        goal: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compare this week's ASR to last week's.
        Returns the delta and business value framing.
        """
        this_week = self.get_asr_trend(target_model, days=7, goal=goal)
        last_week = self.get_asr_trend(target_model, days=14, goal=goal)
        last_week = [r for r in last_week if r not in this_week]

        if not this_week:
            return {"status": "insufficient_data", "message": "No campaigns this week"}

        current_asr = sum(r["asr"] for r in this_week) / len(this_week)

        if not last_week:
            return {
                "status": "no_baseline",
                "current_asr": current_asr,
                "message": "No prior week data for comparison",
            }

        previous_asr = sum(r["asr"] for r in last_week) / len(last_week)
        delta = current_asr - previous_asr
        pct_change = (
            ((previous_asr - current_asr) / previous_asr * 100)
            if previous_asr > 0
            else 0
        )

        if delta < 0:
            framing = f"ASR dropped from {previous_asr:.1f}% to {current_asr:.1f}% — risk reduced {abs(pct_change):.0f}%"
            business_value = f"A single breach could cost $5M+ in fines and lost customers. This week's improvement represents a {abs(pct_change):.0f}% reduction in that exposure."
        elif delta > 0:
            framing = f"⚠️ ASR increased from {previous_asr:.1f}% to {current_asr:.1f}% — risk increased {pct_change:.0f}%"
            business_value = "Regression detected. Immediate remediation recommended before production deployment."
        else:
            framing = f"ASR held steady at {current_asr:.1f}% — no regression detected"
            business_value = (
                "System maintained consistent robustness. Continue monitoring."
            )

        return {
            "status": "ok",
            "current_asr": round(current_asr, 2),
            "previous_asr": round(previous_asr, 2),
            "delta": round(delta, 2),
            "pct_change": round(pct_change, 1),
            "framing": framing,
            "business_value": business_value,
            "this_week_campaigns": len(this_week),
            "last_week_campaigns": len(last_week),
        }

    def get_latest_campaign(self, target_model: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT job_id, asr, robustness_rating, completed_at
                FROM campaigns WHERE target_model = ?
                ORDER BY completed_at DESC LIMIT 1
                """,
                (target_model,),
            ).fetchone()
        if not row:
            return None
        return {
            "job_id": row[0],
            "asr": row[1],
            "robustness_rating": row[2],
            "completed_at": row[3],
        }


# Global singleton
history = CampaignHistory()
