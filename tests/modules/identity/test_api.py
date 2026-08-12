from uuid import uuid4
from fastapi.testclient import TestClient
from decisionos.core.security.principals import get_current_user
from decisionos.main import app

def test_openapi_exposes_identity_endpoints() -> None:
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    assert any(path.startswith("/identity") or path.startswith("/auth") for path in schema["paths"])


def test_swagger_ui_is_available() -> None:
    client = TestClient(app)
    assert client.get("/docs").status_code == 200


def test_me_returns_authenticated_user() -> None:
    user_id = uuid4()
    
    # Override the dependency that retrieves the current user ID
    # We apply the override directly to the app instance
    app.dependency_overrides[get_current_user] = lambda: user_id
    
    try:
        client = TestClient(app)
        response = client.get("/auth/me")
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(user_id)
