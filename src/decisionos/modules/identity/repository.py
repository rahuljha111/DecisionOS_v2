from sqlalchemy.ext.asyncio import AsyncSession

from decisionos.core.database.repository import BaseRepository
from decisionos.modules.identity.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_one(User.email == email.lower())

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_one(User.username == username)
