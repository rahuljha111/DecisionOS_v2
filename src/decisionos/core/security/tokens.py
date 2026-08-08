from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from decisionos.core.config.settings import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_token(subject: UUID, role: str, token_type: str, expires_minutes: int) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(subject),
            "role": role,
            "type": token_type,
            "iat": now,
            "exp": now + timedelta(minutes=expires_minutes),
        },
        settings.jwt_secret_key,
        algorithm="HS256",
    )


def create_access_token(subject: UUID, role: str) -> str:
    return create_token(subject, role, ACCESS_TOKEN_TYPE, settings.jwt_access_token_expire_minutes)


def decode_token(token: str, expected_type: str) -> dict[str, object]:
    claims = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=["HS256"],
        options={"require": ["sub", "exp", "type"]},
    )
    if claims["type"] != expected_type:
        raise jwt.InvalidTokenError("Unexpected token type")
    return claims
