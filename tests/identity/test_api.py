from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from decisionos.core.security.dependencies import get_current_user
from decisionos.main import app
from decisionos.modules.identity.models import User


def test_openapi_exposes_identity_endpoints() -> None:
    schema = TestClient(app).get("/openapi.json").json()
    assert "/identity/register" in schema["paths"]
    assert "/identity/login" in schema["paths"]
    assert "/auth/me" in schema["paths"]


def test_swagger_ui_is_available() -> None:
    assert TestClient(app).get("/docs").status_code == 200


def test_me_returns_authenticated_user() -> None:
    user = User(
        id=uuid4(),
        email="user@example.com",
        username="user",
        full_name="Test User",
        password_hash="hash",
        role="member",
        is_active=True,
        email_verified=False,
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = TestClient(app).get("/auth/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["full_name"] == "Test User"
