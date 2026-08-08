"""Aggregated application router.

New modules register their routers here; the app only ever mounts this one
router, keeping the include list in one place.
"""

from fastapi import APIRouter

from decisionos.core.health.routes import router as health_router
from decisionos.modules.identity.router import auth_router
from decisionos.modules.identity.router import router as identity_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(identity_router)
api_router.include_router(auth_router)
