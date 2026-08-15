from decisionos.core.database.base import Base
from decisionos.modules.knowledge.models import KnowledgeDocument, KnowledgeChunk


def test_knowledge_document_table_has_expected_columns() -> None:
    columns = KnowledgeDocument.__table__.columns

    assert KnowledgeDocument.__tablename__ == "knowledge_documents"
    assert {"id", "created_at", "updated_at"}.issubset(columns.keys())
    assert {
        "workspace_id",
        "title",
        "filename",
        "content_type",
        "status",
        "content_hash",
        "doc_metadata",
    }.issubset(columns.keys())


def test_knowledge_chunk_table_has_expected_columns() -> None:
    columns = KnowledgeChunk.__table__.columns

    assert KnowledgeChunk.__tablename__ == "knowledge_chunks"
    assert {"id", "created_at", "updated_at"}.issubset(columns.keys())
    assert {
        "document_id",
        "chunk_index",
        "content",
        "content_hash",
        "page_number",
        "section_text",
        "embedding_dimensions",
    }.issubset(columns.keys())


def test_knowledge_document_model_is_registered_with_application_metadata() -> None:
    assert KnowledgeDocument.__table__ in Base.metadata.tables.values()


def test_knowledge_chunk_model_is_registered_with_application_metadata() -> None:
    assert KnowledgeChunk.__table__ in Base.metadata.tables.values()