"""Tests for RAG service.

These tests use mocks for the embedding provider and Qdrant vector store
to test the RAG service logic independently.
"""

from uuid import UUID, uuid4

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from decisionos.core.exceptions import ServiceError, ForbiddenError
from decisionos.core.security.principals import Principal

from decisionos.modules.rag.schemas import RagSearchRequest, RagSearchResult, RagSearchResponse
from decisionos.modules.rag.service import RagService
from decisionos.modules.knowledge.embedding import EmbeddingProvider


@pytest.fixture
def mock_embedding_provider():
    """Provide a mock embedding provider."""
    provider = MagicMock(spec=EmbeddingProvider)
    provider.model_name = "test-model"
    provider.dimensions = 384
    provider.embed = AsyncMock(return_value=[0.1] * 384)
    provider.embed_batch = AsyncMock(return_value=[[0.1] * 384] * 10)
    return provider


@pytest.fixture
def mock_session(sample_principal):
    """Provide a mock SQLAlchemy session with required methods."""
    session = MagicMock()
    # The repository.get_by_id calls session.get(model, id)
    # We need to mock this for the workspace service check
    # Return workspace where owner matches the provided principal
    async def mock_get(model, id):
        return MagicMock(owner_id=sample_principal.id)
    session.get = AsyncMock(side_effect=mock_get)
    return session


@pytest.fixture
def mock_qdrant_vector_store():
    """Provide a mock QdrantVectorStore."""
    store = MagicMock()
    return store


@pytest.fixture
def rag_service(mock_embedding_provider, mock_session, mock_qdrant_vector_store):
    """Provide a RagService instance with mocked dependencies."""
    from qdrant_client import QdrantClient

    # Patch QdrantClient at the module level in service.py
    with patch("decisionos.modules.rag.service.QdrantClient") as mock_client:
        mock_client.return_value = mock_qdrant_vector_store
        service = RagService(
            session=mock_session,
            embedding_provider=mock_embedding_provider,
            qdrant_host="localhost",
            qdrant_port=6333,
            collection_name="test_collection",
        )
        # Replace the vector_store with our mock after init
        service.vector_store = mock_qdrant_vector_store
        return service


@pytest.fixture
def sample_principal():
    """Provide a sample authenticated principal."""
    return Principal(id=uuid4(), role="user", permissions=frozenset(["rag:search"]))


@pytest.fixture
def sample_request():
    """Provide a sample RAG search request."""
    return RagSearchRequest(query="test query", top_k=5, score_threshold=0.5)
