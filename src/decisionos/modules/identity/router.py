from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from decisionos.core.database.session import get_db
from decisionos.core.security.dependencies import get_current_user
from decisionos.core.security.principals import Principal
from decisionos.core.security.tokens import create_access_token
from decisionos.modules.identity.models import User
from decisionos.modules.identity.schemas import LoginRequest, TokenResponse, UserRead, UserRegister
from decisionos.modules.identity.service import IdentityService

router = APIRouter(prefix="/identity", tags=["identity"])
auth_router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: UserRegister, session: Annotated[AsyncSession, Depends(get_db)]) -> User:
    return await IdentityService(session).register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest, session: Annotated[AsyncSession, Depends(get_db)]
) -> TokenResponse:
    user = await IdentityService(session).authenticate(str(data.email), data.password)
    return TokenResponse(access_token=create_access_token(user.id, user.role))


@auth_router.get("/me", response_model=UserRead)
async def get_me(
    principal: Annotated[Principal, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    return await IdentityService(session).get_user(principal.id)
