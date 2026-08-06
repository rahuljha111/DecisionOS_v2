from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from decisionos.core.config.settings import settings


def create_access_token(user_id: UUID, role: str) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }
    return jwt.encode(claims, settings.jwt_secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, object]:
    return jwt.decode(
        token, settings.jwt_secret_key, algorithms=["HS256"], options={"require": ["sub", "exp"]}
    )
