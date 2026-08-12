from uuid import UUID

from fastapi import FastAPI

from decisionos.api.routes import api_router
from decisionos.core.config.settings import settings
from decisionos.core.database.session import SessionLocal
from decisionos.core.exceptions import register_exception_handlers
from decisionos.core.logging import configure_logging
from decisionos.core.middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    configure_security_middleware,
)
from decisionos.core.rate_limit import register_rate_limiter
from decisionos.core.security.principals import Principal, register_principal_loader
from decisionos.modules.identity.repository import UserRepository

# Import models to ensure they are registered with Base.metadata
from decisionos.modules.identity.models import User as _User  # noqa: F401
from decisionos.modules.workspaces.models import Workspace as _Workspace  # noqa: F401
from decisionos.modules.decisions.models import Decision as _Decision  # noqa: F401

from decisionos.modules.workspaces.router import router as workspace_router
from decisionos.modules.decisions.router import router as decision_router


async def load_identity_principal(user_id: UUID) -> Principal | None:
    async with SessionLocal() as session:
        user = await UserRepository(session).get_by_id(user_id)
        if user is None or not user.is_active:
            return None
        return Principal(id=user.id, role=user.role)


def create_app() -> FastAPI:
    configure_logging()
    register_principal_loader(load_identity_principal)

    app = FastAPI(title=settings.app_name, version=settings.api_version, debug=settings.debug)
    register_exception_handlers(app)

    # Middleware is stacked last-in-first-out: the final add is the outermost.
    # Rate limiting sits innermost (so 429s are still logged with a request id);
    # CORS and trusted-host filtering are outermost.
    register_rate_limiter(app)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    configure_security_middleware(app, allowed_origins=settings.cors_origins)

    app.include_router(api_router)
    app.include_router(workspace_router, prefix="/workspaces", tags=["workspaces"])
    app.include_router(decision_router, prefix="/decisions", tags=["decisions"])
    return app


app = create_app()
