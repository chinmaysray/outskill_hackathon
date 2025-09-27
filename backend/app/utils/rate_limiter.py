import time
import asyncio
from typing import Dict, Any
from collections import defaultdict, deque
import structlog

logger = structlog.get_logger(__name__)

class RateLimiter:
    """Token bucket rate limiter for API endpoints."""

    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.clients: Dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow_request(self, client_id: str) -> bool:
        """Check if request should be allowed for client."""
        async with self._lock:
            now = time.time()
            client_requests = self.clients[client_id]

            # Remove old requests outside time window
            while client_requests and client_requests[0] <= now - self.time_window:
                client_requests.popleft()

            # Check if under limit
            if len(client_requests) < self.max_calls:
                client_requests.append(now)
                return True

            logger.warning("Rate limit exceeded", client_id=client_id)
            return False

    def get_stats(self, client_id: str) -> Dict[str, Any]:
        """Get rate limiting stats for client."""
        client_requests = self.clients.get(client_id, deque())
        now = time.time()
        recent_requests = sum(1 for req_time in client_requests if req_time > now - self.time_window)

        return {
            "requests_in_window": recent_requests,
            "max_requests": self.max_calls,
            "window_seconds": self.time_window,
            "remaining": max(0, self.max_calls - recent_requests)
        }
