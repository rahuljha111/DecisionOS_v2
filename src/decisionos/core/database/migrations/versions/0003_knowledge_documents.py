"""create knowledge_documents and knowledge_chunks tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-12 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create knowledge_documents table
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("file_path", sa.String(length=2048), nullable=True),
        sa.Column("content_type", sa.String(128), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="uploaded",
        ),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("doc_metadata", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], name=op.f("fk_knowledge_documents_workspace_id_workspaces")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_documents")),
    )
    op.create_index(
        op.f("ix_knowledge_documents_workspace_id"),
        "knowledge_documents",
        ["workspace_id"],
    )

    # Create knowledge_chunks table
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section_text", sa.String(512), nullable=True),
        sa.Column("embedding_dimensions", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["document_id"], ["knowledge_documents.id"], name=op.f("fk_knowledge_chunks_document_id_knowledge_documents")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_chunks")),
    )
    op.create_index(
        op.f("ix_knowledge_chunks_document_id"),
        "knowledge_chunks",
        ["document_id"],
    )
    op.create_index(
        op.f("ix_knowledge_chunks_content_hash"),
        "knowledge_chunks",
        ["content_hash"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_knowledge_chunks_content_hash"),
        table_name="knowledge_chunks",
    )
    op.drop_index(
        op.f("ix_knowledge_chunks_document_id"),
        table_name="knowledge_chunks",
    )
    op.drop_table("knowledge_chunks")
    op.drop_index(
        op.f("ix_knowledge_documents_workspace_id"),
        table_name="knowledge_documents",
    )
    op.drop_table("knowledge_documents")