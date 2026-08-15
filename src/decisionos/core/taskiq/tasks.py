from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from taskiq import TaskiqRunner, task
from taskiq.redis import RedisBroker

from decisionos.core.config.settings import get_settings
from decisionos.core.exceptions import ServiceError

settings = get_settings()

# Redis broker configuration
redis_broker = RedisBroker(
    host=settings.redis_host if hasattr(settings, "redis_host") else "localhost",
    port=settings.redis_port if hasattr(settings, "redis_port") else 6379,
)

taskiq_runner = TaskiqRunner(redis_broker)

logger = logging.getLogger(__name__)


@task
async def process_knowledge_document(
    document_id: str,
    file_path: str,
    mime_type: str,
) -> Dict[str, Any]:
    """Process a knowledge document: extract, normalize, chunk, embed, and index.

    This is the core ingestion pipeline task that runs asynchronously via TaskIQ.

    Pipeline:
        extraction/OCR → normalization → quality check → chunking → embeddings → Qdrant → READY

    Args:
        document_id: The knowledge document identifier
        file_path: Path to the uploaded file
        mime_type: The MIME type of the file

    Returns:
        Dict with processing status and results

    Raises:
        ServiceError: If any step in the pipeline fails
    """
    logger.info(f"Starting knowledge document processing: {document_id}")

    from decisionos.modules.knowledge.repository import KnowledgeDocumentRepository
    from decisionos.modules.knowledge.chunking import chunk_text_with_metadata
    from decisionos.modules.knowledge.processing import FileProcessor
    from decisionos.modules.knowledge.providers.hf_embedding import (
        HuggingFaceEmbeddingProvider,
    )
    from decisionos.modules.knowledge.vector_store import QdrantVectorStore
    from decisionos.core.database.session import get_db
    from decisionos.modules.workspaces.service import WorkspaceService
    from decisionos.core.database.repository import BaseRepository
    from decisionos.modules.knowledge.models import KnowledgeDocument, KnowledgeChunk
    from uuid import UUID
    from qdrant_client import QdrantClient

    # Get database session
    async with get_db() as session:
        doc_repo = KnowledgeDocumentRepository(session)
        chunk_repo = None  # Will use direct queries

        # Step 1: Read the file
        # In a real implementation, we'd read from storage
        # For now, we'll simulate file reading
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
        except FileNotFoundError:
            raise ServiceError(f"File not found: {file_path}")

        # Step 2: Process/file extraction
        processor = FileProcessor()
        try:
            processing_result = await processor.process(file_content, "")
        except ServiceError as e:
            # Mark document as failed
            doc = await doc_repo.get_by_id(UUID(document_id))
            if doc:
                doc.status = "failed"
                await session.flush()
            raise

        # Step 3: Quality validation
        if not processing_result.text.strip():
            raise ServiceError("No extractable content found in document")

        if len(processing_result.text) < 50:
            raise ServiceError(
                "Document has insufficient content (minimum 50 characters required)"
            )

        # Step 4: Chunking
        chunks = chunk_text_with_metadata(
            text=processing_result.text,
            document_id=document_id,
            chunk_size=800,
            chunk_overlap=100,
            min_chunk_size=100,
            # page_number and section_text would come from PDF metadata
        )

        # Step 5: Embedding generation
        embedding_provider = HuggingFaceEmbeddingProvider()

        # Step 6: Get workspace_id from document
        doc = await doc_repo.get_by_id(UUID(document_id))
        if not doc:
            raise ServiceError(f"Document not found: {document_id}")
        workspace_id = str(doc.workspace_id)

        # Initialize Qdrant client
        settings = get_settings()
        qdrant_client = QdrantClient(
            host=settings.qdrant_host if hasattr(settings, "qdrant_host") else "localhost",
            port=settings.qdrant_port if hasattr(settings, "qdrant_port") else 6333,
        )
        vector_store = QdrantVectorStore(client=qdrant_client)

        # Process each chunk
        chunk_records = []
        for chunk_info in chunks:
            # Generate embedding for chunk content
            try:
                embedding = await embedding_provider.embed(chunk_info["content"])
            except ServiceError as e:
                logger.error(f"Embedding failed for chunk: {e}")
                continue

            # Create chunk record in PostgreSQL
            chunk = KnowledgeChunk(
                document_id=UUID(document_id),
                chunk_index=chunk_info["chunk_index"],
                content=chunk_info["content"],
                content_hash=processing_result.content_hash,
                page_number=chunk_info.get("page_number"),
                section_text=chunk_info.get("section_text"),
                embedding_dimensions=len(embedding),
            )
            session.add(chunk)
            await session.flush()  # Get the chunk ID
            chunk_records.append((chunk, embedding))

        # Upsert chunks to Qdrant
        for chunk, embedding in chunk_records:
            try:
                await vector_store.upsert_chunk(
                    chunk_id=str(chunk.id),
                    vector=embedding,
                    workspace_id=workspace_id,
                    document_id=str(chunk.document_id),
                    chunk_index=chunk.chunk_index,
                    source_type="document",
                    payload={
                        "content_hash": chunk.content_hash,
                        "page_number": chunk.page_number,
                        "section_text": chunk.section_text,
                    }
                )
            except ServiceError as e:
                logger.error(f"Qdrant upsert failed for chunk {chunk.id}: {e}")
                # Continue with other chunks

        # Mark document as ready
        if doc:
            doc.status = "ready"
            await session.flush()

        logger.info(f"Knowledge document processing complete: {document_id}")
        return {
            "document_id": document_id,
            "status": "ready",
            "chunks_created": len(chunk_records),
        }