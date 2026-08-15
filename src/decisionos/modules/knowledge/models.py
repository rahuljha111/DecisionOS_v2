from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from decisionos.core.database.base import Base
from decisionos.core.database.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from decisionos.modules.workspaces.models import Workspace
    from decisionos.modules.identity.models import User


class KnowledgeDocument(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_documents"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_path: Mapped[str] = mapped_column(String(2048), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(
        SQLEnum(
            "uploaded", "queued", "processing", "ready", "failed",
            name="document_status",
            native_enum=False,
        ),
        default="uploaded",
        nullable=False,
    )
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    
    doc_metadata: Mapped[str | None] = mapped_column(
    "metadata",
    Text,
    nullable=True,
    key="doc_metadata",
    )

    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk",
        backref="document",
        cascade="all, delete-orphan",
    )

    __table_args__ = {
        "schema": None,
    }

    __repr_fields__ = ["id", "title", "status", "workspace_id"]


class KnowledgeChunk(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_chunks"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_documents.id"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    page_number: Mapped[int | None] = mapped_column(nullable=True)
    section_text: Mapped[str | None] = mapped_column(String(512), nullable=True)
    embedding_dimensions: Mapped[int | None] = mapped_column(nullable=True)

    __table_args__ = {
        "schema": None,
    }

    __repr_fields__ = ["id", "document_id", "chunk_index", "content_hash"]