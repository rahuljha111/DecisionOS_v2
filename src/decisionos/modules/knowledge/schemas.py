from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgeDocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    filename: str = Field(..., min_length=1, max_length=512)
    content_type: str | None = Field(None, max_length=128)
    metadata: dict | None = Field(
        None, description="Additional document metadata"
    )


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    pass


class KnowledgeDocumentRead(KnowledgeDocumentBase):
    id: UUID
    workspace_id: UUID
    status: str
    content_hash: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeDocumentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=512)
    metadata: dict | None = None


class KnowledgeChunkBase(BaseModel):
    chunk_index: int = Field(..., ge=0)
    content: str = Field(..., min_length=1)
    content_hash: str = Field(..., min_length=40, max_length=64)
    page_number: int | None = Field(None, ge=1)
    section_text: str | None = Field(None, max_length=512)


class KnowledgeChunkCreate(KnowledgeChunkBase):
    document_id: UUID


class KnowledgeChunkRead(KnowledgeChunkBase):
    id: UUID
    document_id: UUID

    model_config = {"from_attributes": True}