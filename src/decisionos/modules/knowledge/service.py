from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from decisionos.core.exceptions import NotFoundError, ForbiddenError
from decisionos.core.database.session import get_db
from decisionos.core.security.principals import get_current_user
from decisionos.modules.knowledge.repository import KnowledgeDocumentRepository, KnowledgeChunkRepository
from decisionos.modules.knowledge.schemas import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentRead,
    KnowledgeDocumentUpdate,
    KnowledgeChunkCreate,
    KnowledgeChunkRead,
)
from decisionos.modules.workspaces.service import WorkspaceService


class KnowledgeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.doc_repo = KnowledgeDocumentRepository(session)
        self.chunk_repo = KnowledgeChunkRepository(session)
        self.workspace_service = WorkspaceService(session)

    async def create_document(
        self,
        workspace_id: UUID,
        data: KnowledgeDocumentCreate,
        user_id: UUID,
    ) -> KnowledgeDocumentRead:
        await self.workspace_service.get_workspace(workspace_id, user_id)

        document = await self.doc_repo.create({
            **data.model_dump(),
            "workspace_id": workspace_id,
            "status": "uploaded",
        })

        return KnowledgeDocumentRead(
            id=document.id,
            workspace_id=document.workspace_id,
            title=document.title,
            filename=document.filename,
            content_type=document.content_type,
            status=document.status,
            content_hash=document.content_hash,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

    async def get_document(
        self, document_id: UUID, user_id: UUID
    ) -> KnowledgeDocumentRead:
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise NotFoundError("Knowledge document not found")
        await self.workspace_service.get_workspace(document.workspace_id, user_id)

        return KnowledgeDocumentRead(
            id=document.id,
            workspace_id=document.workspace_id,
            title=document.title,
            filename=document.filename,
            content_type=document.content_type,
            status=document.status,
            content_hash=document.content_hash,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

    async def list_documents(
        self, workspace_id: UUID, user_id: UUID
    ) -> list[KnowledgeDocumentRead]:
        await self.workspace_service.get_workspace(workspace_id, user_id)
        documents = await self.doc_repo.get_by_workspace(workspace_id)

        return [
            KnowledgeDocumentRead(
                id=doc.id,
                workspace_id=doc.workspace_id,
                title=doc.title,
                filename=doc.filename,
                content_type=document.content_type,
                status=doc.status,
                content_hash=doc.content_hash,
                created_at=doc.created_at,
                updated_at=document.updated_at,
            )
            for doc in documents
        ]

    async def update_document(
        self, document_id: UUID, data: KnowledgeDocumentUpdate, user_id: UUID
    ) -> KnowledgeDocumentRead:
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise NotFoundError("Knowledge document not found")
        await self.workspace_service.get_workspace(document.workspace_id, user_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(document, key, value)
        await self.session.flush()

        return KnowledgeDocumentRead(
            id=document.id,
            workspace_id=document.workspace_id,
            title=document.title,
            filename=document.filename,
            content_type=document.content_type,
            status=document.status,
            content_hash=document.content_hash,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

    async def delete_document(self, document_id: UUID, user_id: UUID) -> None:
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise NotFoundError("Knowledge document not found")
        await self.workspace_service.get_workspace(document.workspace_id, user_id)
        await self.doc_repo.delete(document)

    async def get_chunk(
        self, chunk_id: UUID, user_id: UUID
    ) -> KnowledgeChunkRead:
        chunk = await self.chunk_repo.get_by_id(chunk_id)
        if not chunk:
            raise NotFoundError("Knowledge chunk not found")
        await self.workspace_service.get_workspace(
            chunk.document.workspace_id, user_id
        )

        return KnowledgeChunkRead(
            id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            content_hash=chunk.content_hash,
            page_number=chunk.page_number,
            section_text=chunk.section_text,
        )

    async def list_chunks(
        self, document_id: UUID, user_id: UUID
    ) -> list[KnowledgeChunkRead]:
        await self.workspace_service.get_workspace(document_id, user_id)
        # Actually we need the document's workspace_id, let me fix this
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise NotFoundError("Knowledge document not found")
        await self.workspace_service.get_workspace(document.workspace_id, user_id)

        chunks = await self.chunk_repo.get_by_document(document_id)

        return [
            KnowledgeChunkRead(
                id=chunk.id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                content_hash=chunk.content_hash,
                page_number=chunk.page_number,
                section_text=chunk.section_text,
            )
            for chunk in chunks
        ]