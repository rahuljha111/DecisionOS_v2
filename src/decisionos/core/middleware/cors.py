"""HTTP security middleware configuration (CORS + trusted hosts)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from decisionos.core.config.settings import settings


def configure_security_middleware(app: FastAPI, allowed_origins: list[str]) -> None:
    # CORS: browsers enforce this; it does not prevent non-browser clients.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # Host header validation prevents DNS-rebinding attacks. Only enforced when
    # an explicit allow-list is provided (production).
    if settings.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
