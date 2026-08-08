"""Probe endpoints used by orchestrators and load balancers.

Three probes with distinct purposes, all exempt from rate limiting so monitors
never receive a 429:

* ``GET /live``   – process liveness; always 200 while the worker runs.
* ``GET /ready``  – readiness; 200 only when all dependencies are reachable.
* ``GET /health`` – detailed report for dashboards (status + per-service latency).
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine

from decisionos.core.database.session import get_engine
from decisionos.core.health.service import ServiceHealth, check_database
from decisionos.core.rate_limit import limiter

router = APIRouter(tags=["health"])

EngineDep = Annotated[AsyncEngine, Depends(get_engine)]


def _service_payload(service: ServiceHealth) -> dict[str, object]:
    return {"status": "ok" if service.healthy else "degraded", "latency_ms": service.latency_ms}


@limiter.exempt
@router.get("/live", summary="Liveness probe")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@limiter.exempt
@router.get("/ready", summary="Readiness probe")
async def readiness(engine: EngineDep) -> JSONResponse:
    database = await check_database(engine)
    healthy = database.healthy
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={
            "status": "ok" if healthy else "degraded",
            "services": {"database": _service_payload(database)},
        },
    )


@limiter.exempt
@router.get("/health", summary="Health report")
async def health_report(engine: EngineDep) -> dict[str, object]:
    database = await check_database(engine)
    healthy = database.healthy
    return {
        "status": "ok" if healthy else "degraded",
        "services": {"database": _service_payload(database)},
    }
