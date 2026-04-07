"""
RTK-1 Audit Trail — every attack, decision, and score is recorded.
Immutable append-only SQLite log. Never deleted, never modified.
"""

import json
import sqlite3
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("audit")


class AuditEventType(str, Enum):
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_COMPLETED = "campaign_completed"
    CAMPAIGN_FAILED = "campaign_failed"
    SEQUENCE_STARTED = "sequence_started"
    SEQUENCE_COMPLETED = "sequence_completed"
    SEQUENCE_FAILED = "sequence_failed"
    SUPERVISOR_DECISION = "supervisor_decision"
    SCORER_GENERATED = "scorer_generated"
    REPORT_GENERATED = "report_generated"
    ASR_SPIKE_DETECTED = "asr_spike_detected"
    ALERT_SENT = "alert_sent"
    CI_GATE_PASSED = "ci_gate_passed"
    CI_GATE_FAILED = "ci_gate_failed"
    HUMAN_APPROVAL_REQUESTED = "human_approval_requested"
    HUMAN_APPROVED = "human_approved"
    HUMAN_REJECTED = "human_rejected"


class AuditTrail:
    """Append-only audit log for all RTK-1 events."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.audit_db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    campaign_id TEXT,
                    job_id TEXT,
                    timestamp TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    environment TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaign_id
                ON audit_log(campaign_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_type
                ON audit_log(event_type)
            """)
            conn.commit()

    def log(
        self,
        event_type: AuditEventType,
        actor: str,
        payload: Dict[str, Any],
        campaign_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> str:
        import uuid

        event_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO audit_log
                (event_id, event_type, campaign_id, job_id, timestamp, actor, payload, environment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    event_type.value,
                    campaign_id,
                    job_id,
                    timestamp,
                    actor,
                    json.dumps(payload),
                    settings.environment,
                ),
            )
            conn.commit()

        logger.info(
            "audit_event",
            event_id=event_id,
            event_type=event_type.value,
            campaign_id=campaign_id,
            actor=actor,
        )
        return event_id

    def get_campaign_events(self, campaign_id: str) -> list:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM audit_log WHERE campaign_id = ? ORDER BY timestamp",
                (campaign_id,),
            ).fetchall()
        return rows


# Global singleton
audit = AuditTrail()
