from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from decisionos.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from decisionos.core.security.passwords import hash_password, verify_password
from decisionos.modules.identity.models import User
from decisionos.modules.identity.repository import UserRepository
from decisionos.modules.identity.schemas import UserRegister


class IdentityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def register(self, data: UserRegister) -> User:
        if await self.users.get_by_email(str(data.email)) or await self.users.get_by_username(
            data.username
        ):
            raise ConflictError("Email or username is already registered")
        user = await self.users.create(
            {
                "email": str(data.email).lower(),
                "username": data.username,
                "full_name": data.full_name,
                "password_hash": hash_password(data.password),
            }
        )
        await self.session.commit()
        return user

    async def get_user(self, user_id: UUID) -> User:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.users.get_by_email(email)
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")
        user.last_login_at = datetime.now(UTC)
        await self.session.commit()
        return user
