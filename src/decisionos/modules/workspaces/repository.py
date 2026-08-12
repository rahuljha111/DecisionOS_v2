from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decisionos.core.database.repository import BaseRepository
from decisionos.modules.workspaces.models import Workspace
from uuid import UUID

class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Workspace)

    async def get_by_owner(self, owner_id: UUID) -> list[Workspace]:
        stmt = select(Workspace).where(Workspace.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
