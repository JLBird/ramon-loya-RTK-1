"""
RTK-1 Subscription Tier Management — Objective 83
McAfee-style subscription enforcement with JWT token + tier lookup.
Tiers: Starter | Professional | Enterprise | Federal
"""

import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger("subscription")

DB_PATH = "rtk1_subscriptions.db"


class SubscriptionTier(str, Enum):
    STARTER = "starter"  # $2,000/month
    PROFESSIONAL = "professional"  # $8,000/month
    ENTERPRISE = "enterprise"  # $25,000/month
    FEDERAL = "federal"  # $50,000/month


TIER_LIMITS = {
    SubscriptionTier.STARTER: {
        "monthly_price_usd": 2000,
        "max_campaigns_per_month": 10,
        "max_providers": 3,
        "allowed_providers": ["pyrit", "garak", "promptfoo"],
        "federated": False,
        "ndaa_package": False,
        "isac_integration": False,
        "mtls": False,
        "description": "Starter — 10 campaigns/month, 3 providers",
    },
    SubscriptionTier.PROFESSIONAL: {
        "monthly_price_usd": 8000,
        "max_campaigns_per_month": -1,  # unlimited
        "max_providers": 5,
        "allowed_providers": ["pyrit", "garak", "promptfoo", "crewai", "deepteam"],
        "federated": False,
        "ndaa_package": False,
        "isac_integration": False,
        "mtls": False,
        "description": "Professional — unlimited campaigns, 5 providers",
    },
    SubscriptionTier.ENTERPRISE: {
        "monthly_price_usd": 25000,
        "max_campaigns_per_month": -1,
        "max_providers": -1,  # all
        "allowed_providers": ["*"],
        "federated": True,
        "ndaa_package": True,
        "isac_integration": False,
        "mtls": False,
        "description": "Enterprise — multi-node, federated, NDAA package",
    },
    SubscriptionTier.FEDERAL: {
        "monthly_price_usd": 50000,
        "max_campaigns_per_month": -1,
        "max_providers": -1,
        "allowed_providers": ["*"],
        "federated": True,
        "ndaa_package": True,
        "isac_integration": True,
        "mtls": True,
        "description": "Federal — AI-ISAC integration, mTLS, VDP package",
    },
}


class Subscription(BaseModel):
    customer_id: str
    tier: SubscriptionTier
    api_key: str = Field(default_factory=lambda: f"rtk1-{uuid.uuid4().hex[:32]}")
    active: bool = True
    campaigns_this_month: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: Optional[datetime] = None
    billing_email: Optional[str] = None


class SubscriptionManager:
    """Enforces subscription tier limits on all RTK-1 API calls."""

    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    customer_id TEXT PRIMARY KEY,
                    tier TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    active INTEGER DEFAULT 1,
                    campaigns_this_month INTEGER DEFAULT 0,
                    created_at TEXT,
                    expires_at TEXT,
                    billing_email TEXT
                )
            """)
            conn.commit()

    def create_subscription(
        self,
        customer_id: str,
        tier: SubscriptionTier,
        billing_email: Optional[str] = None,
    ) -> Subscription:
        """Create a new subscription and return it with generated API key."""
        sub = Subscription(
            customer_id=customer_id,
            tier=tier,
            expires_at=datetime.now(UTC) + timedelta(days=30),
            billing_email=billing_email,
        )
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO subscriptions
                (customer_id, tier, api_key, active, campaigns_this_month,
                 created_at, expires_at, billing_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    sub.customer_id,
                    sub.tier.value,
                    sub.api_key,
                    1,
                    0,
                    sub.created_at.isoformat(),
                    sub.expires_at.isoformat() if sub.expires_at else None,
                    sub.billing_email,
                ),
            )
            conn.commit()

        logger.info(
            "subscription_created",
            customer_id=customer_id,
            tier=tier.value,
        )
        return sub

    def check_campaign_allowed(self, customer_id: str) -> dict:
        """
        Check if a customer is allowed to run a campaign.
        Returns {allowed: bool, reason: str, tier: str, remaining: int|-1}
        """
        sub = self._load(customer_id)
        if not sub:
            return {
                "allowed": False,
                "reason": "No active subscription found.",
                "tier": None,
            }

        if not sub.active:
            return {
                "allowed": False,
                "reason": "Subscription inactive.",
                "tier": sub.tier,
            }

        if sub.expires_at and datetime.now(UTC) > sub.expires_at:
            return {
                "allowed": False,
                "reason": "Subscription expired.",
                "tier": sub.tier,
            }

        limits = TIER_LIMITS[sub.tier]
        max_campaigns = limits["max_campaigns_per_month"]

        if max_campaigns != -1 and sub.campaigns_this_month >= max_campaigns:
            return {
                "allowed": False,
                "reason": f"Monthly campaign limit ({max_campaigns}) reached for {sub.tier} tier.",
                "tier": sub.tier,
                "remaining": 0,
            }

        return {
            "allowed": True,
            "reason": "OK",
            "tier": sub.tier,
            "remaining": -1
            if max_campaigns == -1
            else max_campaigns - sub.campaigns_this_month,
            "limits": limits,
        }

    def increment_campaign_count(self, customer_id: str) -> None:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                UPDATE subscriptions
                SET campaigns_this_month = campaigns_this_month + 1
                WHERE customer_id = ?
            """,
                (customer_id,),
            )
            conn.commit()

    def get_tier_info(self, tier: SubscriptionTier) -> dict:
        return TIER_LIMITS[tier]

    def get_subscription(self, customer_id: str) -> Optional[Subscription]:
        return self._load(customer_id)

    def _load(self, customer_id: str) -> Optional[Subscription]:
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT * FROM subscriptions WHERE customer_id = ?", (customer_id,)
            ).fetchone()
        if not row:
            return None
        return Subscription(
            customer_id=row[0],
            tier=SubscriptionTier(row[1]),
            api_key=row[2],
            active=bool(row[3]),
            campaigns_this_month=row[4],
            created_at=datetime.fromisoformat(row[5]),
            expires_at=datetime.fromisoformat(row[6]) if row[6] else None,
            billing_email=row[7],
        )


# ── Singleton ─────────────────────────────────────────────────────────────────
subscription_manager = SubscriptionManager()
