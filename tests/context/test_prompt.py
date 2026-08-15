"""Tests for PromptTemplate and PromptBuilder."""

from uuid import UUID, uuid4

import pytest

from decisionos.modules.context.prompt import PromptBuilder, PromptTemplate
from decisionos.modules.rag.schemas import RagSearchResult


class TestPromptTemplate:
    """Tests for PromptTemplate."""

    def test_render_basic(self):
        """Basic template rendering with placeholders."""
        template = PromptTemplate(
            name="test",
            version="1.0.0",
            system_instructions="Answer the question: {user_request}",
            placeholder_mapping={"user_request": "What is the capital of France?"},
        )

        rendered = template.render()
        assert "What is the capital of France?" in rendered

    def test_render_multiple_placeholders(self):
        """Template with multiple placeholder types."""
        template = PromptTemplate(
            name="test",
            version="1.0.0",
            system_instructions="Context: {context}\nQuestion: {user_request}",
            placeholder_mapping={
                "context": "This is the context",
                "user_request": "What is the capital of France?",
            },
        )

        rendered = template.render()
        assert "This is the context" in rendered
        assert "What is the capital of France?" in rendered

    def test_render_missing_placeholder_raises(self):
        """Rendering should raise KeyError for missing placeholder."""
        template = PromptTemplate(
            name="test",
            version="1.0.0",
            system_instructions="Answer: {user_request}",
            placeholder_mapping={},
        )

        try:
            template.render()
            assert False, "Should have raised KeyError"
        except KeyError:
            pass


class TestPromptBuilder:
    """Tests for PromptBuilder."""

    def test_build_basic(self):
        """Basic prompt building from RAG results and user request."""
        builder = PromptBuilder(max_tokens=200)

        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Paris is the capital of France",
                similarity_score=0.95,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
        ]

        user_request = "What is the capital of France?"
        result = builder.build(chunks, user_request)

        assert "prompt" in result
        assert "context_info" in result
        assert "template_name" in result
        assert "template_version" in result
        assert result["prompt"]  # Should have content

    def test_build_with_default_template(self):
        """Building prompt with default template should work."""
        builder = PromptBuilder()

        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Test content for the prompt",
                similarity_score=0.9,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
        ]

        user_request = "Tell me about this content"
        result = builder.build(chunks, user_request)

        assert result["prompt"] is not None
        assert len(result["prompt"]) > 0

    def test_build_sets_template_and_context(self):
        """Building should set template name and context info."""
        builder = PromptBuilder()

        chunks = [
            RagSearchResult(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="Content",
                similarity_score=0.9,
                chunk_index=0,
                source_type="document",
                metadata={},
            ),
        ]

        user_request = "Test request"
        result = builder.build(chunks, user_request)

        assert result["template_name"] == "default"
        assert result["template_version"] == "1.0.0"
        assert "context_info" in result
        assert "chunks" in result["context_info"]