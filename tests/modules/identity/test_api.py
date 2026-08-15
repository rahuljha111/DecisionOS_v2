from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from decisionos.core.security.dependencies import get_current_user
from decisionos.core.security.principals import Principal
from decisionos.main import app


def test_openapi_exposes_identity_endpoints() -> None:
    client = TestClient(app)
    schema = client.get("/openapi.json").json()

    assert any(
        path.startswith("/identity") or path.startswith("/auth")
        for path in schema["paths"]
    )


def test_swagger_ui_is_available() -> None:
    client = TestClient(app)

    assert client.get("/docs").status_code == 200
