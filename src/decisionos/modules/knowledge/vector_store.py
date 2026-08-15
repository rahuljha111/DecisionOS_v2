from __future__ import annotations

from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    Range,
)

from decisionos.core.exceptions import ServiceError
from decisionos.modules.knowledge.schemas import KnowledgeChunkRead


QDRANT_DEFAULT_COLLECTION = "decisionos_knowledge"
QDRANT_VECTOR_SIZE = 384
QDRANT_DISTANCE_METRIC = Distance.COSINE


class QdrantVectorStore:
    """Vector storage integration using Qdrant.

    Handles collection management and vector operations (upsert, search,
    delete) for knowledge chunks. Workspace filtering is enforced through
    payload metadata.

    Architecture:
        - One shared collection with payload-based filtering
        - Collection name is configurable
        - Vectors stored with workspace_id, document_id, chunk_id metadata
    """

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str = QDRANT_DEFAULT_COLLECTION,
        vector_size: int = QDRANT_VECTOR_SIZE,
        distance: Distance = QDRANT_DISTANCE_METRIC,
    ) -> None:
        self.client = client
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance

    async def ensure_collection(self) -> None:
        """Create the collection if it doesn't exist.

        Configures the vector params based on the configured dimensions.
        """
        try:
            collections = await self.client.get_collections()
            existing = [c.name for c in collections.result]

            if self.collection_name not in existing:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=self.distance,
                    ),
                )
                # Create payload indexes for frequently filtered fields
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="workspace_id",
                    field_type="keyword",
                )
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_id",
                    field_type="keyword",
                )
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="chunk_id",
                    field_type="keyword",
                )
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="source_type",
                    field_type="keyword",
                )
        except Exception as e:
            raise ServiceError(f"Qdrant collection setup failed: {e}")

    async def upsert_chunk(
        self,
        chunk_id: str,
        vector: List[float],
        workspace_id: str,
        document_id: str,
        chunk_index: int,
        source_type: str = "document",
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Upsert a chunk's vector into Qdrant.

        Args:
            chunk_id: Unique identifier for the chunk
            vector: The embedding vector
            workspace_id: The workspace identifier
            document_id: The document identifier
            chunk_index: The chunk index within the document
            source_type: Type of source (document, web, etc.)
            payload: Additional metadata to store
        """
        await self.ensure_collection()

        base_payload = {
            "chunk_id": chunk_id,
            "workspace_id": workspace_id,
            "document_id": document_id,
            "chunk_index": chunk_index,
            "source_type": source_type,
        }

        if payload:
            base_payload.update(payload)

        point = PointStruct(
            id=chunk_id,
            vector=vector,
            payload=base_payload,
        )

        try:
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )
        except Exception as e:
            raise ServiceError(f"Qdrant upsert failed: {e}")

    async def search(
        self,
        vector: List[float],
        workspace_id: str,
        limit: int = 10,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors within a workspace.

        Args:
            vector: The query embedding vector
            workspace_id: The workspace to search within (isolation)
            limit: Maximum number of results to return
            filter_conditions: Additional filter conditions

        Returns:
            List of search results with payload and score
        """
        await self.ensure_collection()

        # Always filter by workspace_id for isolation
        must_filter = [
            FieldCondition(key="workspace_id", match={"value": workspace_id})
        ]

        if filter_conditions:
            # Merge additional filters
            for key, value in filter_conditions.items():
                must_filter.append(
                    FieldCondition(key=key, match={"value": value}
                    if isinstance(value, str) else {"value": value})
                )

        try:
            search_result = await self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=limit,
                query_filter=Filter(must=must_filter) if must_filter else None,
                with_payload=True,
                with_vectors=False,
            )

            return [
                {
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload,
                }
                for point in search_result
            ]
        except Exception as e:
            raise ServiceError(f"Qdrant search failed: {e}")

    async def delete_by_document(
        self, document_id: str, workspace_id: str
    ) -> None:
        """Delete all chunks associated with a document.

        Args:
            document_id: The document identifier
            workspace_id: The workspace identifier
        """
        await self.ensure_collection()

        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=[
                    {"filter": {
                        "must": [
                            {"key": "document_id", "match": {"value": document_id}},
                            {"key": "workspace_id", "match": {"value": workspace_id}},
                        ]
                    }}
                ],
            )
        except Exception as e:
            raise ServiceError(f"Qdrant delete by document failed: {e}")

    async def delete_by_workspace(self, workspace_id: str) -> None:
        """Delete all chunks within a workspace.

        Args:
            workspace_id: The workspace identifier
        """
        await self.ensure_collection()

        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=[
                    {"filter": {
                        "must": [
                            {"key": "workspace_id", "match": {"value": workspace_id}},
                        ]
                    }}
                ],
            )
        except Exception as e:
            raise ServiceError(f"Qdrant delete by workspace failed: {e}")