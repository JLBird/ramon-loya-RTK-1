"""
RTK-1 Per-Customer Rate Limiter — sliding window, SQLite-backed.
Prevents API abuse and enables tiered customer pricing enforcement.
"""

import sqlite3
import time
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("rate_limiter")


class RateLimiter:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.campaign_db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    customer_id TEXT NOT NULL,
                    window_start REAL NOT NULL,
                    request_count INTEGER DEFAULT 1,
                    PRIMARY KEY (customer_id, window_start)
                )
            """)
            conn.commit()

    def check_and_increment(
        self,
        customer_id: str,
        max_requests: int = 10,
        window_seconds: int = 3600,
    ) -> dict:
        """
        Check if customer is within rate limit and increment counter.
        Returns allowed=True/False with current usage stats.
        """
        now = time.time()
        window_start = now - window_seconds

        with sqlite3.connect(self.db_path) as conn:
            # Clean old windows
            conn.execute(
                "DELETE FROM rate_limits WHERE window_start < ?", (window_start,)
            )

            # Count current window requests
            row = conn.execute(
                """
                SELECT SUM(request_count) FROM rate_limits
                WHERE customer_id = ? AND window_start >= ?
                """,
                (customer_id, window_start),
            ).fetchone()
            current_count = row[0] or 0

            allowed = current_count < max_requests

            if allowed:
                conn.execute(
                    """
                    INSERT INTO rate_limits (customer_id, window_start, request_count)
                    VALUES (?, ?, 1)
                    ON CONFLICT(customer_id, window_start)
                    DO UPDATE SET request_count = request_count + 1
                    """,
                    (customer_id, now),
                )
                conn.commit()

        logger.info(
            "rate_limit_checked",
            customer_id=customer_id,
            current_count=current_count,
            max_requests=max_requests,
            allowed=allowed,
        )

        return {
            "customer_id": customer_id,
            "allowed": allowed,
            "current_count": current_count,
            "max_requests": max_requests,
            "window_seconds": window_seconds,
            "requests_remaining": max(0, max_requests - current_count),
        }

    def get_status(self, customer_id: str, window_seconds: int = 3600) -> dict:
        """Get current rate limit status without incrementing."""
        now = time.time()
        window_start = now - window_seconds
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT SUM(request_count) FROM rate_limits
                WHERE customer_id = ? AND window_start >= ?
                """,
                (customer_id, window_start),
            ).fetchone()
        current_count = row[0] or 0
        return {
            "customer_id": customer_id,
            "current_count": current_count,
            "requests_remaining": max(0, 10 - current_count),
            "window_seconds": window_seconds,
        }


rate_limiter = RateLimiter()
