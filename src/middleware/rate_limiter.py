"""
Rate limiting middleware using token bucket algorithm.
"""
from fastapi import Request, HTTPException, status
from collections import defaultdict
from typing import Dict, List
import time
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter.
    Tracks requests per IP address and enforces rate limits.
    """
    
    def __init__(self, requests_per_minute: int = None):
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.window_seconds = 60
    
    async def __call__(self, request: Request) -> None:
        """Check if request should be rate limited."""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Clean old requests outside the time window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > window_start
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                extra={"ip": client_ip, "limit": self.requests_per_minute}
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
            )
        
        # Add current request timestamp
        self.requests[client_ip].append(current_time)
        logger.debug(
            f"Request allowed for IP: {client_ip}",
            extra={
                "ip": client_ip,
                "requests_in_window": len(self.requests[client_ip])
            }
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxy headers."""
        # Check for forwarded IP (if behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client host
        return request.client.host if request.client else "unknown"


# Create global rate limiter instance
rate_limiter = RateLimiter()
