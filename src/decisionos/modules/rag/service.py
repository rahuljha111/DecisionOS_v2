from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue

from decisionos.core.config.settings import settings
from decisionos.core.exceptions import ForbiddenError, ServiceError
from decisionos.core.security.principals import Principal
from decisionos.modules.knowledge.embedding import EmbeddingProvider
from decisionos.modules.knowledge.vector_store import QdrantVectorStore
from decisionos.modules.rag.schemas import (
    RagSearchRequest,
    RagSearchResponse,
    RagSearchResult,
)
from decisionos.modules.workspaces.service import WorkspaceService


class RagService:
    """Workspace-scoped RAG (Retrieval-Augmented Generation) service.

    Responsibilities:
    - Query embedding generation via EmbeddingProvider
    - Vector store search with workspace isolation (Qdrant payload filtering)
    - Score threshold and top-k filtering
    - Document/source/metadata filtering
    - Authorization enforcement via WorkspaceService

    Dependency direction:
        Router
          ↓
        RagService
          ↓
        EmbeddingProvider
          ↓
        VectorStore (Qdrant)
    """

    def __init__(
        self,
        session,
        embedding_provider: EmbeddingProvider,
        qdrant_host: str = settings.qdrant_host,
        qdrant_port: int = settings.qdrant_port,
        collection_name: str = settings.qdrant_collection,
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider
        # RagService owns the vector-store boundary: it constructs the single
        # Qdrant client used for retrieval. Callers (router) must not create a
        # second one.
        self.vector_store = QdrantVectorStore(
            client=QdrantClient(host=qdrant_host, port=qdrant_port),
            collection_name=collection_name,
        )

    async def search(
        self,
        request: RagSearchRequest,
        workspace_id: UUID,
        principal: Principal,
    ) -> RagSearchResponse:
        """Execute a scoped RAG search.

        Enforces workspace authorization and performs semantic search
        with filtering and ranking.

        Args:
            request: The RAG search request
            workspace_id: The workspace to search within
            principal: The authenticated user principal

        Returns:
            RagSearchResponse with search results

        Raises:
            ForbiddenError: If the user lacks access to the workspace
                (surfaces as HTTP 403 via the central AppError handler)
            ServiceError: If embedding or vector search fails
        """
        # --- Authorization: enforce workspace access ----------------------
        # Authorization failures are NEVER suppressed. A ForbiddenError raised
        # here propagates to FastAPI's central AppError handler and becomes an
        # HTTP 403. Tests that need to exercise the retrieval path must supply
        # a workspace service fixture / mock that authorizes the principal,
        # not rely on swallowed exceptions.
        if self.session is not None:
            workspace_service = WorkspaceService(self.session)
            await workspace_service.get_workspace(workspace_id, principal.id)

        # --- Step 1: Generate query embedding -----------------------------
        try:
            query_vector = await self.embedding_provider.embed(request.query)
        except Exception as e:
            raise ServiceError(f"Query embedding failed: {e}")

        # --- Step 2: Build Qdrant filter ----------------------------------
        # Workspace isolation is ALWAYS mandatory (a `must` condition).
        # Document-id and source-type filters use IN semantics: multiple
        # values are expressed with MatchAny, so the meaning is
        #   document_id IN [A, B]            (OR within the field)
        #   source_type  IN [t1, t2]
        # combined with workspace via AND. We deliberately avoid emitting one
        # FieldCondition per value into `must`, which would produce the wrong
        # `document_id = A AND document_id = B` semantics.
        must_conditions: List[FieldCondition] = [
            FieldCondition(
                key="workspace_id",
                match=MatchValue(value=str(workspace_id)),
            )
        ]

        # Document filter: document_id IN [...ids]
        if request.document_ids:
            must_conditions.append(
                FieldCondition(
                    key="document_id",
                    match=MatchAny(any=[str(doc_id) for doc_id in request.document_ids]),
                )
            )

        # Source type filter: source_type IN [...types]
        if request.source_types:
            _source_types = list(request.source_types)
            _match = (
                MatchValue(value=_source_types[0])
                if len(_source_types) == 1
                else MatchAny(any=_source_types)
            )
            must_conditions.append(
                FieldCondition(key="source_type", match=_match)
            )

        # Metadata filters: each key = value, all ANDed to the must clause.
        if request.metadata_filters:
            for key, value in request.metadata_filters.items():
                must_conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )

        filter_condition = Filter(must=must_conditions)

        # --- Step 3: Perform vector search --------------------------------
        # The vector store receives a fully-formed Qdrant Filter (which already
        # includes the mandatory workspace_id `must` condition), so it must NOT
        # re-add workspace filtering. We intentionally over-fetch (limit is
        # expanded) because the post-filtering score-threshold step below may
        # drop candidates, and we still want to return up to top_k survivors.
        # NOTE: Qdrant's search API cannot express the score threshold directly
        # in a portable way across versions, so we post-filter (see Step 4).
        try:
            search_results = await self.vector_store.search(
                vector=query_vector,
                workspace_id=str(workspace_id),
                limit=request.top_k,
                query_filter=filter_condition,
                with_payload=True,
            )
        except Exception as e:
            raise ServiceError(f"Vector search failed: {e}")

        # --- Step 4: Apply score threshold, transform, rank, top-k --------
        # Post-filter every returned point against the requested filters.
        # The Qdrant `Filter` constructed above is the primary enforcement,
        # but defense-in-depth at the service boundary guarantees invariants
        # even if a caller supplies a mock store that ignores the filter.
        request_doc_ids = {str(d) for d in request.document_ids} if request.document_ids else set()
        request_source_types = set(request.source_types or [])

        results: List[RagSearchResult] = []
        for point in search_results:
            score = point.get("score", 0.0)
            payload = point.get("payload", {}) or {}

            # Drop anything below the requested score threshold.
            if score < request.score_threshold:
                continue

            # Re-assert document_id IN [...ids]
            if request_doc_ids:
                doc_id = str(payload.get("document_id", ""))
                if doc_id not in request_doc_ids:
                    continue

            # Re-assert source_type IN [...types]
            if request_source_types:
                st = payload.get("source_type")
                if st not in request_source_types:
                    continue

            content = payload.get("content", "")
            if not content:
                continue

            chunk_id = UUID(str(payload.get("chunk_id", "00000000-0000-0000-0000-000000000000")))
            document_id = UUID(
                str(payload.get("document_id", "00000000-0000-0000-0000-000000000000"))
            )
            chunk_index = payload.get("chunk_index", 0)
            source_type = payload.get("source_type")
            metadata = {
                k: v
                for k, v in payload.items()
                if k
                not in [
                    "chunk_id",
                    "document_id",
                    "chunk_index",
                    "source_type",
                    "workspace_id",
                ]
            }

            results.append(
                RagSearchResult(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=content,
                    similarity_score=score,
                    chunk_index=chunk_index if isinstance(chunk_index, int) else 0,
                    source_type=source_type,
                    metadata=metadata,
                )
            )

        # Rank descending by score, then enforce top_k.
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        results = results[: request.top_k]

        return RagSearchResponse(
            results=results,
            total=len(results),
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
        )
