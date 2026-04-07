"""
RTK-1 Regulatory Change Tracker — monitors EU AI Act and NIST updates.
Flags when compliance mappings may need to be updated.
No API calls required — uses cached known framework versions.
"""

import sqlite3
from datetime import UTC, datetime
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("regulatory")

# Known framework versions and their key requirements
# Updated manually when frameworks publish new guidance
FRAMEWORK_REGISTRY = {
    "eu_ai_act": {
        "current_version": "2024/1689",
        "enforcement_date": "2026-08-02",
        "key_articles": {
            "Article 9": "Risk management system — ongoing adversarial testing required",
            "Article 15": "Accuracy, robustness, cybersecurity — quantified ASR evidence",
            "Annex IV": "Technical documentation — full campaign records required",
            "Article 72": "Post-market monitoring — continuous testing obligation",
        },
        "recent_guidance": [
            {
                "date": "2025-01-01",
                "title": "GPAI Code of Practice — Draft 1",
                "impact": "General purpose AI models now require adversarial testing documentation",
                "rtk1_action": "Ensure report includes GPAI coverage section",
            },
        ],
        "last_checked": "2026-04-05",
    },
    "nist_ai_rmf": {
        "current_version": "1.0",
        "key_functions": {
            "GOVERN 1.2": "AI risk policies established",
            "MAP 5.1": "Likelihood and impact identified",
            "MEASURE 2.7": "AI trustworthiness evaluated with adversarial testing",
            "MANAGE 4.1": "Residual risk documented",
        },
        "last_checked": "2026-04-05",
    },
    "owasp_llm": {
        "current_version": "2025",
        "top_risks": {
            "LLM01": "Prompt Injection",
            "LLM02": "Insecure Output Handling",
            "LLM06": "Sensitive Information Disclosure",
            "LLM08": "Excessive Agency",
        },
        "last_checked": "2026-04-05",
    },
}


class RegulatoryTracker:
    """
    Tracks regulatory framework versions and flags outdated mappings.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.campaign_db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS regulatory_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    framework TEXT NOT NULL,
                    update_title TEXT NOT NULL,
                    update_date TEXT NOT NULL,
                    impact TEXT NOT NULL,
                    rtk1_action TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0,
                    recorded_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def get_compliance_summary(self) -> Dict:
        """
        Returns current compliance framework status for report generation.
        """
        eu_act = FRAMEWORK_REGISTRY["eu_ai_act"]
        enforcement = datetime.fromisoformat(eu_act["enforcement_date"])
        days_until = (enforcement - datetime.now(UTC)).days

        return {
            "eu_ai_act": {
                "version": eu_act["current_version"],
                "enforcement_date": eu_act["enforcement_date"],
                "days_until_enforcement": max(0, days_until),
                "urgency": "ACTIVE"
                if days_until <= 0
                else f"{days_until} days until enforcement",
                "key_articles": eu_act["key_articles"],
            },
            "nist_ai_rmf": {
                "version": FRAMEWORK_REGISTRY["nist_ai_rmf"]["current_version"],
                "key_functions": FRAMEWORK_REGISTRY["nist_ai_rmf"]["key_functions"],
            },
            "owasp_llm": {
                "version": FRAMEWORK_REGISTRY["owasp_llm"]["current_version"],
                "top_risks": FRAMEWORK_REGISTRY["owasp_llm"]["top_risks"],
            },
            "generated_at": datetime.now(UTC).isoformat(),
        }

    def get_pending_actions(self) -> List[Dict]:
        """Returns list of RTK-1 actions needed based on recent guidance."""
        actions = []
        for framework, data in FRAMEWORK_REGISTRY.items():
            for guidance in data.get("recent_guidance", []):
                actions.append({
                    "framework": framework,
                    "date": guidance["date"],
                    "title": guidance["title"],
                    "impact": guidance["impact"],
                    "action_required": guidance["rtk1_action"],
                })
        return actions

    def add_regulatory_update(
        self,
        framework: str,
        title: str,
        update_date: str,
        impact: str,
        rtk1_action: str,
    ) -> None:
        """Manually add a new regulatory update when discovered."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO regulatory_updates
                (framework, update_title, update_date, impact,
                 rtk1_action, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    framework,
                    title,
                    update_date,
                    impact,
                    rtk1_action,
                    datetime.now(UTC).isoformat(),
                ),
            )
            conn.commit()
        logger.info("regulatory_update_added", framework=framework, title=title)


# Global singleton
regulatory = RegulatoryTracker()
