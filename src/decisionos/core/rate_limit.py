"""Rate limiting via SlowAPI.

A single global limiter protects every API route with a configurable default
window. Liveness/readiness probes and documentation are exempt so they never
echo a 429 back to monitors.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from decisionos.core.config.settings import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit] if settings.rate_limit_enabled else [],
    headers_enabled=False,
)
limiter.enabled = settings.rate_limit_enabled


async def _rate_limit_exceeded_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


def register_rate_limiter(app: FastAPI) -> None:
    # SlowAPI middleware reads the live limiter off app.state.
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
