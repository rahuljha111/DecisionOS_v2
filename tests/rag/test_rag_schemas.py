"""Tests for RAG schemas."""

from uuid import UUID, uuid4

import pytest

from decisionos.modules.rag.schemas import (
    RagSearchRequest,
    RagSearchResult,
    RagSearchResponse,
)


class TestRagSearchRequest:
    """Tests for RagSearchRequest."""

    def test_valid_request(self):
        """A valid request should parse correctly."""
        request = RagSearchRequest(
            query="test query",
            top_k=5,
            score_threshold=0.5,
        )
        assert request.query == "test query"
        assert request.top_k == 5
        assert request.score_threshold == 0.5

    def test_valid_request_defaults(self):
        """A request with defaults should use default values."""
        request = RagSearchRequest(query="test query")
        assert request.query == "test query"
        assert request.top_k == 10
        assert request.score_threshold == 0.0

    def test_query_not_empty(self):
        """Empty query should fail validation."""
        from pydantic import ValidationError
        try:
            RagSearchRequest(query="")
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass

    def test_query_whitespace_only(self):
        """Whitespace-only query should fail validation."""
        from pydantic import ValidationError
        try:
            RagSearchRequest(query="   ")
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass

    def test_top_k_bounds(self):
        """top_k out of bounds should fail."""
        from pydantic import ValidationError
        # top_k too small
        try:
            RagSearchRequest(query="test", top_k=0)
            assert False, "Should have raised ValidationError for top_k=0"
        except ValidationError:
            pass

        # top_k too large
        try:
            RagSearchRequest(query="test", top_k=101)
            assert False, "Should have raised ValidationError for top_k=101"
        except ValidationError:
            pass

    def test_score_threshold_bounds(self):
        """score_threshold out of bounds should fail."""
        from pydantic import ValidationError
        try:
            RagSearchRequest(query="test", score_threshold=-0.1)
            assert False, "Should have raised ValidationError for negative threshold"
        except ValidationError:
            pass

        try:
            RagSearchRequest(query="test", score_threshold=1.5)
            assert False, "Should have raised ValidationError for threshold > 1"
        except ValidationError:
            pass


class TestRagSearchResult:
    """Tests for RagSearchResult."""

    def test_valid_result(self):
        """A valid result should parse correctly."""
        result = RagSearchResult(
            chunk_id=uuid4(),
            document_id=uuid4(),
            content="test content",
            similarity_score=0.85,
        )
        assert result.content == "test content"
        assert result.similarity_score == 0.85
        assert result.chunk_index == 0
        assert result.metadata == {}


class TestRagSearchResponse:
    """Tests for RagSearchResponse."""

    def test_valid_response(self):
        """A valid response should parse correctly."""
        results = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="test content",
                similarity_score=0.85,
            )
        ]
        response = RagSearchResponse(
            results=results,
            total=1,
            query="test query",
            top_k=10,
            score_threshold=0.5,
        )
        assert len(response.results) == 1
        assert response.total == 1
        assert response.query == "test query"
        assert response.top_k == 10
        assert response.score_threshold == 0.5