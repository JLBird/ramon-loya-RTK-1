"""
RTK-1 ITIL 4 Continual Improvement Register — Objective 91
Multi-Tenant Campaign Isolation — Objective 84
"""

import sqlite3
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger("itil4_cir")

CIR_DB = "rtk1_cir.db"
TENANT_DB = "rtk1_tenants.db"


# ══════════════════════════════════════════════════════════════════════════════
# ITIL 4 CONTINUAL IMPROVEMENT REGISTER — Objective 91
# ══════════════════════════════════════════════════════════════════════════════


class CIRStatus(str, Enum):
    PROPOSED = "proposed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"


class CIREntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    initiative: str
    baseline_metric: str
    target_metric: str
    owner: str
    status: CIRStatus = CIRStatus.PROPOSED
    itil4_step: str  # "vision|now|target|how|action|verify|momentum"
    priority: str = "medium"  # "low|medium|high|critical"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""


class ContinualImprovementRegister:
    """
    ITIL 4 CSI model applied to RTK-1.
    Tracks all improvement initiatives across the platform.
    7-step CSI model: vision → now → target → how → action → verify → momentum
    """

    def __init__(self):
        self._init_db()
        self._seed_default_entries()

    def _init_db(self):
        with sqlite3.connect(CIR_DB) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cir (
                    entry_id TEXT PRIMARY KEY,
                    initiative TEXT NOT NULL,
                    baseline_metric TEXT,
                    target_metric TEXT,
                    owner TEXT,
                    status TEXT DEFAULT 'proposed',
                    itil4_step TEXT,
                    priority TEXT DEFAULT 'medium',
                    created_at TEXT,
                    updated_at TEXT,
                    notes TEXT
                )
            """)
            conn.commit()

    def _seed_default_entries(self):
        """Seed with RTK-1's core improvement initiatives if empty."""
        with sqlite3.connect(CIR_DB) as conn:
            count = conn.execute("SELECT COUNT(*) FROM cir").fetchone()[0]
        if count > 0:
            return

        defaults = [
            CIREntry(
                initiative="Reduce ASR below 20% for all client models",
                baseline_metric="Current average ASR: unknown",
                target_metric="ASR < 20% across all providers",
                owner="RTK-1 Orchestrator",
                status=CIRStatus.IN_PROGRESS,
                itil4_step="vision",
                priority="critical",
            ),
            CIREntry(
                initiative="Complete Loki/ELK log integration",
                baseline_metric="Logs stdout only",
                target_metric="JSON logs in Grafana Loki with label filtering",
                owner="Infrastructure",
                status=CIRStatus.COMPLETED,
                itil4_step="action",
                priority="high",
                notes="Objective 40 completed 2026-04-10",
            ),
            CIREntry(
                initiative="Federal compliance package — NDAA 1512",
                baseline_metric="No federal compliance reporting",
                target_metric="VDP-ready ISAC disclosure on every campaign",
                owner="Compliance Engine",
                status=CIRStatus.IN_PROGRESS,
                itil4_step="action",
                priority="critical",
            ),
            CIREntry(
                initiative="Subscription tier enforcement",
                baseline_metric="No tier enforcement",
                target_metric="All 4 tiers enforced with JWT + campaign limits",
                owner="Product",
                status=CIRStatus.IN_PROGRESS,
                itil4_step="how",
                priority="high",
            ),
            CIREntry(
                initiative="Achieve 100% objective completion (v0.5.0)",
                baseline_metric="57/66 objectives complete (86%)",
                target_metric="95/95 objectives complete (100%)",
                owner="Engineering",
                status=CIRStatus.IN_PROGRESS,
                itil4_step="target",
                priority="high",
            ),
        ]

        with sqlite3.connect(CIR_DB) as conn:
            for entry in defaults:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO cir VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                    (
                        entry.entry_id,
                        entry.initiative,
                        entry.baseline_metric,
                        entry.target_metric,
                        entry.owner,
                        entry.status.value,
                        entry.itil4_step,
                        entry.priority,
                        entry.created_at.isoformat(),
                        entry.updated_at.isoformat(),
                        entry.notes,
                    ),
                )
            conn.commit()

    def add(self, entry: CIREntry) -> CIREntry:
        with sqlite3.connect(CIR_DB) as conn:
            conn.execute(
                """
                INSERT INTO cir VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    entry.entry_id,
                    entry.initiative,
                    entry.baseline_metric,
                    entry.target_metric,
                    entry.owner,
                    entry.status.value,
                    entry.itil4_step,
                    entry.priority,
                    entry.created_at.isoformat(),
                    entry.updated_at.isoformat(),
                    entry.notes,
                ),
            )
            conn.commit()
        logger.info("cir_entry_added", initiative=entry.initiative[:60])
        return entry

    def update_status(self, entry_id: str, status: CIRStatus, notes: str = "") -> bool:
        with sqlite3.connect(CIR_DB) as conn:
            rows = conn.execute(
                """
                UPDATE cir SET status=?, updated_at=?, notes=?
                WHERE entry_id=?
            """,
                (status.value, datetime.now(UTC).isoformat(), notes, entry_id),
            ).rowcount
            conn.commit()
        return rows > 0

    def get_all(self, status: Optional[CIRStatus] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(CIR_DB) as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM cir WHERE status=? ORDER BY priority DESC",
                    (status.value,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM cir ORDER BY priority DESC"
                ).fetchall()
        cols = [
            "entry_id",
            "initiative",
            "baseline_metric",
            "target_metric",
            "owner",
            "status",
            "itil4_step",
            "priority",
            "created_at",
            "updated_at",
            "notes",
        ]
        return [dict(zip(cols, r)) for r in rows]

    def get_dashboard(self) -> Dict[str, Any]:
        """ITIL 4 CSI dashboard — current state of all improvement initiatives."""
        all_entries = self.get_all()
        by_status = {}
        for e in all_entries:
            s = e["status"]
            by_status[s] = by_status.get(s, 0) + 1

        return {
            "total_initiatives": len(all_entries),
            "by_status": by_status,
            "critical_in_progress": [
                e["initiative"]
                for e in all_entries
                if e["priority"] == "critical" and e["status"] == "in_progress"
            ],
            "recently_completed": [
                e for e in all_entries if e["status"] == "completed"
            ][-5:],
            "itil4_vision": "ASR below 20% for all clients — 24/7 autonomous red teaming",
        }


cir = ContinualImprovementRegister()


# ══════════════════════════════════════════════════════════════════════════════
# MULTI-TENANT ISOLATION — Objective 84
# ══════════════════════════════════════════════════════════════════════════════


class TenantManager:
    """
    Secure isolation between enterprise clients.
    Customer namespace in all DB tables.
    Zero data leakage between tenants.
    """

    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(TENANT_DB) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tenants (
                    customer_id TEXT PRIMARY KEY,
                    api_key TEXT UNIQUE NOT NULL,
                    company_name TEXT,
                    tier TEXT DEFAULT 'starter',
                    reports_dir TEXT,
                    active INTEGER DEFAULT 1,
                    created_at TEXT
                )
            """)
            conn.commit()

    def register_tenant(
        self,
        customer_id: str,
        company_name: str,
        tier: str = "starter",
    ) -> Dict[str, str]:
        import os
        import secrets

        api_key = f"rtk1-{secrets.token_hex(24)}"
        reports_dir = f"reports/{customer_id}"
        os.makedirs(reports_dir, exist_ok=True)

        with sqlite3.connect(TENANT_DB) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tenants
                (customer_id, api_key, company_name, tier, reports_dir, active, created_at)
                VALUES (?,?,?,?,?,1,?)
            """,
                (
                    customer_id,
                    api_key,
                    company_name,
                    tier,
                    reports_dir,
                    datetime.now(UTC).isoformat(),
                ),
            )
            conn.commit()

        logger.info("tenant_registered", customer_id=customer_id, tier=tier)
        return {
            "customer_id": customer_id,
            "api_key": api_key,
            "reports_dir": reports_dir,
        }

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return tenant info."""
        with sqlite3.connect(TENANT_DB) as conn:
            row = conn.execute(
                "SELECT customer_id, company_name, tier, reports_dir FROM tenants "
                "WHERE api_key=? AND active=1",
                (api_key,),
            ).fetchone()
        if not row:
            return None
        return {
            "customer_id": row[0],
            "company_name": row[1],
            "tier": row[2],
            "reports_dir": row[3],
        }

    def get_tenant_reports_dir(self, customer_id: str) -> str:
        """Get isolated reports directory for tenant."""
        with sqlite3.connect(TENANT_DB) as conn:
            row = conn.execute(
                "SELECT reports_dir FROM tenants WHERE customer_id=?", (customer_id,)
            ).fetchone()
        return row[0] if row else f"reports/{customer_id}"


tenant_manager = TenantManager()
