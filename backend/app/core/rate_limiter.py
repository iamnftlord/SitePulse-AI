import asyncio
import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class InMemoryRateLimiter:
    """Thread-safe sliding window in-memory rate limiter per client IP."""

    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60.0
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """
        Evaluates whether a request from client_ip is allowed under the rate limit.
        Returns: (is_allowed: bool, retry_after_seconds: int)
        """
        now = time.monotonic()
        cutoff = now - self.window_seconds

        async with self._lock:
            history = self.requests[client_ip]
            # Prune timestamps older than window
            self.requests[client_ip] = [ts for ts in history if ts > cutoff]

            if len(self.requests[client_ip]) >= self.requests_per_minute:
                oldest = self.requests[client_ip][0]
                retry_after = max(1, int(self.window_seconds - (now - oldest)))
                return False, retry_after

            self.requests[client_ip].append(now)
            return True, 0


rate_limiter = InMemoryRateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing sliding-window rate limits on analysis and audit endpoints."""

    async def dispatch(self, request: Request, call_next):
        # Only rate limit resource-intensive POST endpoints (/api/v1/analyze, /api/audit, /api/v1/chat)
        path = request.url.path
        is_intensive_route = (
            request.method == "POST" and
            any(route in path for route in ("/analyze", "/audit", "/quick-scan", "/chat"))
        )

        if not is_intensive_route or not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Determine client IP (handles X-Forwarded-For if behind reverse proxy/Nginx)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        allowed, retry_after = await rate_limiter.is_allowed(client_ip)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait before submitting more audit requests.",
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        return response
