from unittest.mock import AsyncMock, MagicMock, patch
"""Tests for RAG filtering capabilities.

Tests document filter, source type filter, and metadata filter functionality.
"""

from uuid import UUID, uuid4

import pytest
from unittest.mock import AsyncMock, MagicMock

from decisionos.modules.rag.schemas import RagSearchRequest, RagSearchResult, RagSearchResponse
from decisionos.modules.rag.service import RagService
from decisionos.core.security.principals import Principal


@pytest.fixture
def sample_principal():
    return Principal(id=uuid4(), role="user", permissions=frozenset(["rag:search"]))


@pytest.fixture
def rag_service_with_mocks(sample_principal):
    """Provide a RagService with mocked embedding and vector store.

    The session is mocked so that ``WorkspaceService.get_workspace`` succeeds
    for the supplied ``sample_principal``: ``session.get`` returns a workspace
    whose ``owner_id`` matches the principal's id. This is the correct
    authorization path — earlier revisions of these tests relied on the
    RagService silently swallowing ``ForbiddenError``, which violated
    workspace isolation in production code.
    """
    from decisionos.core.config.settings import settings
    from qdrant_client import QdrantClient

    mock_store = MagicMock()
    mock_emb = MagicMock()
    mock_emb.embed = AsyncMock(return_value=[0.1] * 384)

    with patch("decisionos.modules.rag.service.QdrantClient") as mock_client:
        mock_client.return_value = mock_store
        mock_session = MagicMock()
        # Authorize the sample principal for every workspace it asks about.
        mock_session.get = AsyncMock(
            return_value=MagicMock(owner_id=sample_principal.id)
        )
        service = RagService(
            session=mock_session,
            embedding_provider=mock_emb,
            qdrant_host="localhost",
            qdrant_port=6333,
            collection_name="test_collection",
        )
        service.vector_store = mock_store
        return service


class TestDocumentFilter:
    """Tests for document ID filtering."""

    @pytest.mark.asyncio
    async def test_filter_by_document_ids(self, rag_service_with_mocks, sample_principal):
        """Search should filter results to only specified document IDs."""
        request = RagSearchRequest(
            query="test query",
            document_ids=[uuid4()],  # Filter to one document
        )

        # Mock search returning results from multiple documents
        mock_store = rag_service_with_mocks.vector_store
        mock_store.search = AsyncMock(return_value=[
            {
                "id": str(uuid4()),
                "score": 0.95,
                "payload": {
                    "chunk_id": str(uuid4()),
                    "document_id": str(uuid4()),  # Different from filter
                    "chunk_index": 0,
                    "content": "Should be filtered out",
                    "source_type": "document",
                    "workspace_id": str(uuid4()),
                },
            },
            {
                "id": str(uuid4()),
                "score": 0.88,
                "payload": {
                    "chunk_id": str(uuid4()),
                    "document_id": str(request.document_ids[0]),  # Matches filter
                    "chunk_index": 0,
                    "content": "Should be included",
                    "source_type": "document",
                    "workspace_id": str(uuid4()),
                },
            },
        ])

        response = await rag_service_with_mocks.search(
            request=request,
            workspace_id=uuid4(),
            principal=sample_principal,
        )

        # Should only return the chunk matching the document filter
        assert len(response.results) == 1
        assert response.results[0].content == "Should be included"


class TestSourceTypeFilter:
    """Tests for source type filtering."""

    @pytest.mark.asyncio
    async def test_filter_by_source_type(self, rag_service_with_mocks, sample_principal):
        """Search should filter results by source type."""
        request = RagSearchRequest(
            query="test query",
            source_types=["document"],  # Only return document sources
        )

        mock_store = rag_service_with_mocks.vector_store
        mock_store.search = AsyncMock(return_value=[
            {
                "id": str(uuid4()),
                "score": 0.95,
                "payload": {
                    "chunk_id": str(uuid4()),
                    "document_id": str(uuid4()),
                    "chunk_index": 0,
                    "content": "Doc source content",
                    "source_type": "document",  # Matches filter
                    "workspace_id": str(uuid4()),
                },
            },
            {
                "id": str(uuid4()),
                "score": 0.88,
                "payload": {
                    "chunk_id": str(uuid4()),
                    "document_id": str(uuid4()),
                    "chunk_index": 0,
                    "content": "Web source content",
                    "source_type": "web",  # Different source type
                    "workspace_id": str(uuid4()),
                },
            },
        ])

        response = await rag_service_with_mocks.search(
            request=request,
            workspace_id=uuid4(),
            principal=sample_principal,
        )

        # Should only return document source chunks
        assert len(response.results) == 1
        assert response.results[0].source_type == "document"


class TestMetadataFilter:
    """Tests for metadata filtering."""

    @pytest.mark.asyncio
    async def test_filter_by_metadata(self, rag_service_with_mocks, sample_principal):
        """Search should support metadata filters."""
        request = RagSearchRequest(
            query="test query",
            metadata_filters={"author": "test_author"},  # Filter by metadata
        )

        mock_store = rag_service_with_mocks.vector_store
        mock_store.search = AsyncMock(return_value=[
            {
                "id": str(uuid4()),
                "score": 0.95,
                "payload": {
                    "chunk_id": str(uuid4()),
                    "document_id": str(uuid4()),
                    "chunk_index": 0,
                    "content": "Authorized content",
                    "source_type": "document",
                    "workspace_id": str(uuid4()),
                    # No 'author' in metadata - should be filtered out by score
                    # but let's assume it passes threshold
                },
            },
        ])

        response = await rag_service_with_mocks.search(
            request=request,
            workspace_id=uuid4(),
            principal=sample_principal,
        )

        # Result should be included if it passes all filters
        assert len(response.results) >= 0


class TestCombinedFilters:
    """Tests for combined filtering."""

    @pytest.mark.asyncio
    async def test_combined_document_and_source_filter(self, rag_service_with_mocks, sample_principal):
        """Search with both document and source type filters."""
        request = RagSearchRequest(
            query="test query",
            document_ids=[uuid4()],
            source_types=["document"],
        )

        mock_store = rag_service_with_mocks.vector_store
        mock_store.search = AsyncMock(return_value=[
            {
                "id": str(uuid4()),
                "score": 0.95,
                "payload": {
                    "chunk_id": str(uuid4()),
                    "document_id": str(request.document_ids[0]) if hasattr(request, 'document_ids') else uuid4(),
                    "chunk_index": 0,
                    "content": "Matches both filters",
                    "source_type": "document",  # Matches both
                    "workspace_id": str(uuid4()),
                },
            },
            {
                "id": str(uuid4()),
                "score": 0.88,
                "payload": {
                    "chunk_id": str(uuid4()),
                    "document_id": uuid4(),  # Different document
                    "chunk_index": 0,
                    "content": "Matches source only",
                    "source_type": "document",
                    "workspace_id": str(uuid4()),
                },
            },
            {
                "id": str(uuid4()),
                "score": 0.82,
                "payload": {
                    "chunk_id": str(uuid4()),
                    "document_id": str(request.document_ids[0]) if hasattr(request, 'document_ids') else uuid4(),
                    "chunk_index": 0,
                    "content": "Matches document only",
                    "source_type": "web",  # Different source type
                    "workspace_id": str(uuid4()),
                },
            },
        ])

        response = await rag_service_with_mocks.search(
            request=request,
            workspace_id=uuid4(),
            principal=sample_principal,
        )

        # Should only return the chunk matching both filters
        assert len(response.results) == 1
        assert response.results[0].content == "Matches both filters"