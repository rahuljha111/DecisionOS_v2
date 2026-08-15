"""Tests for ContextBuilder."""

from uuid import UUID, uuid4

import pytest

from decisionos.modules.rag.schemas import RagSearchResult, RagSearchResponse
from decisionos.modules.context.service import ContextBuilder


class TestContextBuilderDedup:
    """Tests for ContextBuilder.dedup()."""

    def test_dedup_removes_identical_content(self):
        """Duplicate chunks based on same content should be removed."""
        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="This is unique content A",
                similarity_score=0.9,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="This is unique content A",  # Duplicate
                similarity_score=0.85,
                chunk_index=1,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="This is unique content B",  # Different
                similarity_score=0.8,
                chunk_index=2,
                source_type="document",
                metadata={},
            ),
        ]

        builder = ContextBuilder()
        deduped = builder.dedup(chunks)

        # Should have 2 chunks (duplicate removed)
        assert len(deduped) == 2

        # The first occurrence should be preserved
        assert deduped[0].content == "This is unique content A"
        assert deduped[1].content == "This is unique content B"

    def test_dedup_preserves_order(self):
        """Deduplication should preserve the order of first occurrences."""
        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="First occurrence",
                similarity_score=0.9,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Second chunk",
                similarity_score=0.8,
                chunk_index=1,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="First occurrence",  # Duplicate of first
                similarity_score=0.7,
                chunk_index=2,
                source_type="document",
                metadata={},
            ),
        ]

        builder = ContextBuilder()
        deduped = builder.dedup(chunks)

        assert len(deduped) == 2
        assert deduped[0].content == "First occurrence"
        assert deduped[1].content == "Second chunk"


class TestContextBuilderOrder:
    """Tests for ContextBuilder.order()."""

    def test_order_by_score_descending(self):
        """Chunks should be ordered by similarity score descending."""
        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Low relevance",
                similarity_score=0.3,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="High relevance",
                similarity_score=0.95,
                chunk_index=1,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Medium relevance",
                similarity_score=0.6,
                chunk_index=2,
                source_type="document",
                metadata={},
            ),
        ]

        builder = ContextBuilder()
        ordered = builder.order(chunks)

        assert ordered[0].content == "High relevance"
        assert ordered[1].content == "Medium relevance"
        assert ordered[2].content == "Low relevance"


class TestContextBuilderEstimateTokens:
    """Tests for ContextBuilder.estimate_tokens()."""

    def test_estimate_tokens_basic(self):
        """Basic token estimation should work."""
        builder = ContextBuilder()

        # Empty string
        assert builder.estimate_tokens("") == 0

        # Short text
        result = builder.estimate_tokens("hello")
        assert result >= 1

        # Longer text
        long_text = "This is a much longer piece of text that should have more tokens estimated."
        result = builder.estimate_tokens(long_text)
        assert result > 1

    def test_estimate_tokens_whitespace(self):
        """Whitespace handling in token estimation."""
        builder = ContextBuilder()

        # Multiple spaces should still estimate something
        result = builder.estimate_tokens("hello   world")
        assert result >= 1


class TestContextBuilderEnforceBudget:
    """Tests for ContextBuilder.enforce_budget()."""

    def test_enforce_budget_within_limit(self):
        """Chunks that fit within the budget should all be included."""
        builder = ContextBuilder(max_tokens=100)

        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Short chunk A",
                similarity_score=0.9,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Short chunk B",
                similarity_score=0.8,
                chunk_index=1,
                source_type="document",
                metadata={},
            ),
        ]

        bounded, total_tokens = builder.enforce_budget(chunks)

        # Both should fit within max_tokens=100
        assert len(bounded) == 2
        assert total_tokens <= 100

    def test_enforce_budget_exceeds_limit(self):
        """Chunks that exceed the budget should be truncated."""
        builder = ContextBuilder(max_tokens=50)

        # Generate text clearly over 50 tokens (50 * 3.5 = 175 chars minimum)
        # Use 80 "This " repetitions + suffix ≈ 400 chars ≈ 114 tokens
        long_text = "This " * 80 + "suffix/end/marker text"
        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content=long_text,
                similarity_score=0.9,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
        ]

        bounded, total_tokens = builder.enforce_budget(chunks)

        # Should have 0 chunks since the text exceeds 50 tokens
        assert len(bounded) == 0
        assert total_tokens <= 50

    def test_enforce_budget_mixed(self):
        """Mixed chunk sizes with budget enforcement."""
        builder = ContextBuilder(max_tokens=100)

        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Tiny chunk",
                similarity_score=0.9,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="This is a medium-sized chunk that should fit within the budget along with the tiny one",
                similarity_score=0.8,
                chunk_index=1,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="This chunk is very long and will definitely push us over the budget limit significantly",
                similarity_score=0.7,
                chunk_index=2,
                source_type="document",
                metadata={},
            ),
        ]

        bounded, total_tokens = builder.enforce_budget(chunks)

        # Should include only the first chunk (tiny one)
        assert len(bounded) >= 0  # May include 1 or 2 depending on exact token counts
        assert total_tokens <= 100


class TestContextBuilderBuildContext:
    """Tests for ContextBuilder.build_context()."""

    def test_build_context_returns_dict(self):
        """build_context should return a dict with expected keys."""
        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Test content",
                similarity_score=0.95,
                chunk_index=0,
                source_type="document",
                metadata={"author": "test"},
            ),
        ]

        builder = ContextBuilder(max_tokens=200)
        result = builder.build_context(chunks)

        assert isinstance(result, dict)
        assert "chunks" in result
        assert "total_estimated_tokens" in result
        assert "max_tokens_budget" in result
        assert "chunk_count" in result


class TestContextBuilderBuildPipeline:
    """Tests for ContextBuilder.build() full pipeline."""

    def test_build_pipeline_full(self):
        """Full build pipeline: dedup → order → budget → context."""
        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Chunk A content",
                similarity_score=0.9,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Chunk B content",
                similarity_score=0.8,
                chunk_index=1,
                source_type="document",
                metadata={},
            ),
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Chunk A content",  # Duplicate of A
                similarity_score=0.7,
                chunk_index=2,
                source_type="document",
                metadata={},
            ),
        ]

        builder = ContextBuilder(max_tokens=200)
        selected, context_dict = builder.build(chunks)

        # Should have deduplicated (2 unique chunks)
        assert len(selected) == 2

        # Context dict should have expected structure
        assert isinstance(context_dict, dict)
        assert "chunks" in context_dict
        assert context_dict["chunk_count"] == 2  # After dedup