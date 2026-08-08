"""Centralized exception handling.

Every business error surfaces as an :class:`AppError` subclass with an agreed
``status_code`` and ``detail``. FastAPI already maps ``HTTPException`` and
``RequestValidationError`` (422) to the same ``{"detail": ...}`` envelope, so we
only register handlers for domain errors and for anything that escapes
unhandled, keeping every response shape consistent.
"""

from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from decisionos.core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base error for expected business conditions (404, 409, 403...)."""

    status_code: int = 500
    detail: str = "An unexpected error occurred"

    def __init__(self, detail: str, *, status_code: int | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


async def _app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    error = cast(AppError, exc)
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Errors escaping every layer are a bug: log the traceback, return a safe,
    # non-leaking body, and let ops correlate it via the request id.
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
