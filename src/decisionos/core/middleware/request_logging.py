"""Request logging middleware.

Emits one structured log line per request with the method, path, status,
duration and request id, so the request lifecycle is observable end to end.
"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from decisionos.core.middleware.request_id import get_request_id

request_logger = logging.getLogger("decisionos.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        request_logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.1f",
            get_request_id(),
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
