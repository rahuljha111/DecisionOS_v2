from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from decisionos.core.config.settings import settings
from decisionos.core.database.session import get_db
from decisionos.core.security.dependencies import get_current_user
from decisionos.core.security.principals import Principal

from decisionos.modules.knowledge.embedding import EmbeddingProvider, get_embedding_provider
from decisionos.modules.rag.schemas import RagSearchRequest, RagSearchResponse
from decisionos.modules.rag.service import RagService

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post(
    "/workspaces/{workspace_id}/search",
    response_model=RagSearchResponse,
    status_code=status.HTTP_200_OK,
)
async def rag_search(
    workspace_id: UUID,
    request: RagSearchRequest,
    session=Depends(get_db),
    principal: Principal = Depends(get_current_user),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
) -> RagSearchResponse:
    """Execute a workspace-scoped semantic search over Knowledge.

    Retrieves the most relevant knowledge chunks for a given query,
    enforced within the requesting user's workspace authorization.

    Authentication:
        JWT bearer token required. Principal must have access to the
        specified workspace.

    Body:
        - query: The search query text
        - top_k: Maximum number of results (default: 10, max: 100)
        - score_threshold: Minimum similarity score (0-1, default: 0.0)

    Path Parameters:
        - workspace_id: The workspace to search within

    Returns:
        RagSearchResponse with ranked results including chunk content,
        document IDs, similarity scores, and metadata.

    Dependency flow:
        Router
          -> RagService
               -> EmbeddingProvider (injected; concrete selection lives in
                  get_embedding_provider, behind the embedding boundary)
               -> QdrantVectorStore (constructed by RagService itself)
    """
    rag_service = RagService(
        session=session,
        embedding_provider=embedding_provider,
        qdrant_host=settings.qdrant_host,
        qdrant_port=settings.qdrant_port,
        collection_name=settings.qdrant_collection,
    )

    return await rag_service.search(request, workspace_id, principal)
