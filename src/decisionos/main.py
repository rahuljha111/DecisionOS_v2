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
    return app


app = create_app()
