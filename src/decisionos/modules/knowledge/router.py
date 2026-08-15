from uuid import UUID

from fastapi import APIRouter, Depends, status, UploadFile, File
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from decisionos.core.database.session import get_db
from decisionos.core.security.principals import get_current_user
from decisionos.modules.knowledge.service import KnowledgeService
from decisionos.modules.knowledge.schemas import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentRead,
    KnowledgeDocumentUpdate,
    KnowledgeChunkCreate,
    KnowledgeChunkRead,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post(
    "/workspaces/{workspace_id}/documents",
    response_model=KnowledgeDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    workspace_id: UUID,
    data: KnowledgeDocumentCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)],
):
    return await KnowledgeService(session).create_document(
        workspace_id, data, user
    )


@router.post(
    "/workspaces/{workspace_id}/documents/upload",
    response_model=KnowledgeDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    workspace_id: UUID,
    file: Annotated[UploadFile, File(...)],
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)],
):
    import magic

    content_type = magic.from_buffer(file.file.read(1024), mime=True)
    file.file.seek(0)

    document_create = KnowledgeDocumentCreate(
        title=file.filename,
        filename=file.filename,
        content_type=content_type,
    )

    return await KnowledgeService(session).create_document(
        workspace_id, document_create, user
    )


@router.get("/workspaces/{workspace_id}/documents", response_model=list[KnowledgeDocumentRead])
async def list_documents(
    workspace_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)],
):
    return await KnowledgeService(session).list_documents(workspace_id, user)


@router.get(
    "/workspaces/{workspace_id}/documents/{document_id}",
    response_model=KnowledgeDocumentRead,
)
async def get_document(
    workspace_id: UUID,
    document_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)],
):
    return await KnowledgeService(session).get_document(document_id, user)


@router.patch(
    "/workspaces/{workspace_id}/documents/{document_id}",
    response_model=KnowledgeDocumentRead,
)
async def update_document(
    workspace_id: UUID,
    document_id: UUID,
    data: KnowledgeDocumentUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)],
):
    return await KnowledgeService(session).update_document(
        document_id, data, user
    )


@router.delete(
    "/workspaces/{workspace_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    workspace_id: UUID,
    document_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)],
):
    await KnowledgeService(session).delete_document(document_id, user)


@router.get(
    "/workspaces/{workspace_id}/documents/{document_id}/chunks",
    response_model=list[KnowledgeChunkRead],
)
async def list_chunks(
    workspace_id: UUID,
    document_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)],
):
    return await KnowledgeService(session).list_chunks(document_id, user)