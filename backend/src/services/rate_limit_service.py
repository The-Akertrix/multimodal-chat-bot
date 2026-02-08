from collections import deque
from datetime import datetime, timedelta
from typing import Deque, Dict

REQUEST_LIMIT: int = 10
WINDOW_SECONDS: int = 60


class RateLimitService:
    """Simple in-memory rate limiter."""

    def __init__(self) -> None:
        """Initialize rate limiter storage."""
        self.user_requests: Dict[str, Deque[datetime]] = {}

    def check_rate_limit(self, user_id: str) -> None:
        """Check and enforce rate limit for user.

        Args:
            user_id: Identifier of requesting user.

        Raises:
            Exception: When user exceeded rate limit.
        """
        now: datetime = datetime.utcnow()
        window_start: datetime = now - timedelta(seconds=WINDOW_SECONDS)

        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()

        request_queue: Deque[datetime] = self.user_requests[user_id]

        while request_queue and request_queue[0] < window_start:
            request_queue.popleft()

        if len(request_queue) >= REQUEST_LIMIT:
            raise Exception("Rate limit exceeded")

        request_queue.append(now)
