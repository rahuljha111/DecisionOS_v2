from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from decisionos.core.security.principals import Principal, load_principal
from decisionos.core.security.tokens import ACCESS_TOKEN_TYPE, decode_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> Principal:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    try:
        claims = decode_token(credentials.credentials, ACCESS_TOKEN_TYPE)
        principal = await load_principal(UUID(str(claims["sub"])))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token"
        ) from error
    if principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or unknown user"
        )
    return principal


def require_permission(*permissions: str) -> Callable:
    async def dependency(principal: Annotated[Principal, Depends(get_current_user)]) -> Principal:
        if not set(permissions).issubset(principal.permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return principal

    return dependency


def require_role(*roles: str) -> Callable:
    async def dependency(principal: Annotated[Principal, Depends(get_current_user)]) -> Principal:
        if principal.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return principal

    return dependency
