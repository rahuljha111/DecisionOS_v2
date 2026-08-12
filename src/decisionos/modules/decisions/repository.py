from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decisionos.core.database.repository import BaseRepository
from decisionos.modules.decisions.models import Decision
from uuid import UUID

class DecisionRepository(BaseRepository[Decision]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Decision)

    async def get_by_workspace(self, workspace_id: UUID) -> list[Decision]:
        stmt = select(Decision).where(Decision.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
