"""
VoiceFlow AI — Middleware
Rate limiting, tenant isolation, request logging, and audit trail.
"""

import time
import logging
from typing import Callable
from uuid import UUID

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import settings
from src.core.redis import cache

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token-bucket rate limiting per IP using Redis."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ("/api/v1/health", "/docs", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{client_ip}"

        try:
            count = await cache.increment(key, expire=60)
            if count > settings.rate_limit_per_minute:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded. Please try again later."},
                )
        except Exception:
            # If Redis is down, allow the request through
            pass

        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with timing information."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            "%s %s → %s (%.3fs)",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        return response


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Extract tenant_id from JWT and inject into request state."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Tenant context is set by auth dependencies, this middleware
        # ensures the state object is always available
        request.state.tenant_id = None
        request.state.user_id = None
        request.state.user_role = None
        return await call_next(request)


def setup_middleware(app: FastAPI) -> None:
    """Register all middleware on the FastAPI application."""
    # CORS — must be added first
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware (order matters — last added runs first)
    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
