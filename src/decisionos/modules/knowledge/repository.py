from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from decisionos.core.database.repository import BaseRepository
from decisionos.modules.knowledge.models import KnowledgeDocument, KnowledgeChunk


class KnowledgeDocumentRepository(BaseRepository[KnowledgeDocument]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, KnowledgeDocument)

    async def get_by_workspace(self, workspace_id: UUID) -> list[KnowledgeDocument]:
        stmt = select(KnowledgeDocument).where(KnowledgeDocument.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, workspace_id: UUID, status: str) -> list[KnowledgeDocument]:
        stmt = select(KnowledgeDocument).where(
            KnowledgeDocument.workspace_id == workspace_id,
            KnowledgeDocument.status == status,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_ready_documents(self, workspace_id: UUID) -> list[KnowledgeDocument]:
        return await self.get_by_status(workspace_id, "ready")


class KnowledgeChunkRepository(BaseRepository[KnowledgeChunk]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, KnowledgeChunk)

    async def get_by_document(self, document_id: UUID) -> list[KnowledgeChunk]:
        stmt = select(KnowledgeChunk).where(KnowledgeChunk.document_id == document_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_document_and_index(
        self, document_id: UUID, chunk_index: int
    ) -> KnowledgeChunk | None:
        stmt = select(KnowledgeChunk).where(
            KnowledgeChunk.document_id == document_id,
            KnowledgeChunk.chunk_index == chunk_index,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_by_document(
        self, document_id: UUID, limit: int = 10
    ) -> list[KnowledgeChunk]:
        stmt = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.document_id == document_id)
            .order_by(KnowledgeChunk.chunk_index.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())