"""Health checks for core infrastructure services.

Checks return a normalized :class:`ServiceHealth` so callers (the /ready and
/health probes) stay stable. New dependencies (Redis, vector store, message
bus) are added as sibling check functions and surfaced under the same
``services`` dict without touching the routes.
"""

import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class ServiceHealth:
    """Normalized result of a single dependency check."""

    __slots__ = ("name", "healthy", "latency_ms")

    def __init__(self, name: str, healthy: bool, latency_ms: float | None) -> None:
        self.name = name
        self.healthy = healthy
        self.latency_ms = latency_ms


async def check_database(engine: AsyncEngine) -> ServiceHealth:
    """Verify the database accepts connections with a cheap ``SELECT 1``."""
    start = time.perf_counter()
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        return ServiceHealth(name="database", healthy=False, latency_ms=None)
    return ServiceHealth(
        name="database", healthy=True, latency_ms=(time.perf_counter() - start) * 1000
    )
