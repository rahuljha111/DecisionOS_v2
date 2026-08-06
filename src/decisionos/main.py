from fastapi import FastAPI

from decisionos.core.config.settings import settings
from decisionos.core.middleware.cors import configure_security_middleware
from decisionos.modules.identity.router import auth_router
from decisionos.modules.identity.router import router as identity_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")
    configure_security_middleware(app, allowed_origins=[])
    app.include_router(identity_router)
    app.include_router(auth_router)
    return app


app = create_app()
