import pytest

from decisionos.modules.knowledge.chunking import (
    chunk_text,
    chunk_text_with_metadata,
)


def test_chunk_text_basic():
    """Test basic text chunking."""
    text = "This is a test sentence. " * 50

    chunks = chunk_text(
        text,
        chunk_size=100,
        chunk_overlap=20,
    )

    assert len(chunks) > 1

    for index, chunk in chunks:
        assert isinstance(index, int)
        assert isinstance(chunk, str)
        assert len(chunk.strip()) > 0


def test_chunk_text_empty():
    """Test chunking with empty text."""
    chunks = chunk_text("")
    assert chunks == []


def test_chunk_text_minimum():
    """Test chunking with text below minimum chunk size."""
    text = "Short text"
    chunks = chunk_text(text, min_chunk_size=100)

    assert isinstance(chunks, list)


def test_chunk_text_with_metadata():
    """Test chunking with metadata enrichment."""
    text = "This is a test sentence. " * 50

    chunks = chunk_text_with_metadata(
        text=text,
        document_id="doc-123",
        chunk_size=100,
        chunk_overlap=20,
    )

    assert len(chunks) > 0

    for chunk in chunks:
        assert chunk["document_id"] == "doc-123"
        assert "chunk_index" in chunk
        assert "content" in chunk


def test_chunk_text_very_short():
    """Test chunking with very short text."""
    text = "Hi"
    chunks = chunk_text(text, min_chunk_size=100)

    assert isinstance(chunks, list)