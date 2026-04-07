"""
RTK-1 Per-Customer Rate Limiter — prevents API abuse.
In-memory sliding window per API key / customer ID.
"""

import time
from collections import defaultdict, deque

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("rate_limiter")


class RateLimiter:
    """
    Sliding window rate limiter per customer.
    Thread-safe for async use via asyncio single-thread model.
    """

    def __init__(self, requests_per_minute: int = None):
        self._rpm = requests_per_minute or settings.rate_limit_per_minute
        self._windows: dict[str, deque] = defaultdict(deque)

    def is_allowed(self, customer_id: str) -> bool:
        now = time.time()
        window = self._windows[customer_id]

        # Remove requests older than 60 seconds
        while window and window[0] < now - 60:
            window.popleft()

        if len(window) >= self._rpm:
            logger.warning(
                "rate_limit_exceeded",
                customer_id=customer_id,
                requests_in_window=len(window),
                limit=self._rpm,
            )
            return False

        window.append(now)
        return True

    def get_usage(self, customer_id: str) -> dict:
        now = time.time()
        window = self._windows[customer_id]
        while window and window[0] < now - 60:
            window.popleft()
        return {
            "customer_id": customer_id,
            "requests_last_minute": len(window),
            "limit_per_minute": self._rpm,
            "remaining": max(0, self._rpm - len(window)),
        }

    def reset(self, customer_id: str) -> None:
        self._windows[customer_id].clear()
        logger.info("rate_limit_reset", customer_id=customer_id)


# Global singleton
rate_limiter = RateLimiter()
